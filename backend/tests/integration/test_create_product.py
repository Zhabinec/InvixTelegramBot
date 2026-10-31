
import asyncio
from pathlib import Path
from unittest import IsolatedAsyncioTestCase
from uuid import uuid4

from minio import Minio
from sqlalchemy import delete, select, text

from app.application.use_cases.create_product import (
    CreateProductCommand,
    CreateProductUseCase,
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


class TestCreateProductIntegration(IsolatedAsyncioTestCase):
    async def test_create_product(self) -> None:
        database_settings = DatabaseSettings(postgres_db="shop_test_db")
        minio_settings = MinioSettings()

        engine, session_factory = create_database(database_settings)
        repository = PostgresProductRepository(session_factory)
        storage = MinioImageStorage(minio_settings)

        use_case = CreateProductUseCase(repository, storage)

        client = Minio(
            endpoint=minio_settings.minio_endpoint,
            access_key=minio_settings.minio_root_user,
            secret_key=minio_settings.minio_root_password.get_secret_value(),
            secure=minio_settings.minio_secure,
        )

        image_path = (
            Path(__file__).resolve().parents[1]
            / "fixtures"
            / "product.jpg"
        )

        image_bytes = image_path.read_bytes()
        request_key = RequestKey(f"integration:{uuid4().hex}")

        command = CreateProductCommand(
            title="Integration Test Product",
            image_bytes=image_bytes,
            content_type="image/jpeg",
            request_key=request_key,
        )

        try:
            async with session_factory() as session:
                database_name = await session.scalar(
                    text("SELECT current_database()")
                )

            self.assertEqual(database_name, "shop_test_db")

            product = await use_case.execute(command)

            self.assertEqual(product.status, ProductStatus.READY)
            self.assertEqual(
                product.image_key,
                ImageKey.for_product(product.id),
            )

            repeated = await use_case.execute(command)

            self.assertEqual(repeated.id, product.id)

            products = await repository.list_ready()

            self.assertTrue(
                any(item.id == product.id for item in products)
            )

            metadata = await asyncio.to_thread(
                client.stat_object,
                minio_settings.minio_bucket,
                product.image_key.value,
            )

            self.assertEqual(metadata.size, len(image_bytes))

        finally:
            try:
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
                        client.remove_object,
                        minio_settings.minio_bucket,
                        ImageKey.for_product(product_id).value,
                    )
            finally:
                await engine.dispose()
