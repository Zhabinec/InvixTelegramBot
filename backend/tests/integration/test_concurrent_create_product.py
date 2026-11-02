
import asyncio
from pathlib import Path
from uuid import uuid4

import pytest
from minio import Minio
from sqlalchemy import delete, func, select, text

from app.application.use_cases.create_product import (
    CreateProductCommand,
    CreateProductUseCase,
    ProductConflictError,
)
from app.domain.entities.product import ProductStatus
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.request_key import RequestKey
from app.infrastructure.config import DatabaseSettings, MinioSettings
from app.infrastructure.database.connection import create_database
from app.infrastructure.database.models.product import ProductORM
from app.infrastructure.repositories.postgres_product_repository import (
    PostgresProductRepository,
)
from app.infrastructure.storage.minio_image_storage import MinioImageStorage


@pytest.mark.asyncio
async def test_concurrent_product_creation() -> None:
    database_settings = DatabaseSettings(
        postgres_db="shop_test_db"
    )
    minio_settings = MinioSettings()

    engine, session_factory = create_database(database_settings)

    request_key = RequestKey(f"concurrent:{uuid4().hex}")

    image_path = (
        Path(__file__).resolve().parents[1]
        / "fixtures"
        / "product.jpg"
    )

    command = CreateProductCommand(
        title="Concurrent Test Product",
        image_bytes=image_path.read_bytes(),
        content_type="image/jpeg",
        request_key=request_key,
    )

    minio_client = Minio(
        endpoint=minio_settings.minio_endpoint,
        access_key=minio_settings.minio_root_user,
        secret_key=minio_settings.minio_root_password.get_secret_value(),
        secure=minio_settings.minio_secure,
    )

    database_verified = False

    try:
        async with session_factory() as session:
            database_name = await session.scalar(
                text("SELECT current_database()")
            )

        assert database_name == "shop_test_db", (
            f"Unsafe test database: {database_name}"
        )
        database_verified = True

        async def create_product():
            repository = PostgresProductRepository(session_factory)
            storage = MinioImageStorage(minio_settings)

            use_case = CreateProductUseCase(repository, storage)

            return await use_case.execute(command)

        # Six concurrent requests using independent use cases.
        products = await asyncio.gather(
            *(create_product() for _ in range(6))
        )

        # All requests must return the same product.
        product_ids = {product.id for product in products}

        assert len(product_ids) == 1
        assert all(
            product.status == ProductStatus.READY
            for product in products
        )

        product_id = next(iter(product_ids))

        # Exactly one matching row in PostgreSQL.
        async with session_factory() as session:
            count = await session.scalar(
                select(func.count())
                .select_from(ProductORM)
                .where(
                    ProductORM.request_key == request_key.value
                )
            )

        assert count == 1

        # Same key with different data must be rejected.
        conflict_command = CreateProductCommand(
            title="Different Product",
            image_bytes=command.image_bytes,
            content_type="image/jpeg",
            request_key=request_key,
        )

        with pytest.raises(ProductConflictError):
            await CreateProductUseCase(
                PostgresProductRepository(session_factory),
                MinioImageStorage(minio_settings),
            ).execute(conflict_command)

    finally:
        try:
            if database_verified:
                async with session_factory.begin() as session:
                    product_id = await session.scalar(
                        select(ProductORM.id).where(
                            ProductORM.request_key == request_key.value
                        )
                    )

                    await session.execute(
                        delete(ProductORM).where(
                            ProductORM.request_key == request_key.value
                        )
                    )

                if product_id is not None:
                    await asyncio.to_thread(
                        minio_client.remove_object,
                        minio_settings.minio_bucket,
                        ImageKey.for_product(product_id).value,
                    )
        finally:
            await engine.dispose()
