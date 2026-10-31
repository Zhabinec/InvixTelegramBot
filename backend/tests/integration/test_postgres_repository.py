from unittest import IsolatedAsyncioTestCase

from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import delete, text

from app.domain.entities.product import Product, ProductStatus
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.request_key import RequestKey
from app.infrastructure.config import DatabaseSettings
from app.infrastructure.database.connection import create_database
from app.infrastructure.database.models.product import ProductORM
from app.infrastructure.repositories.postgres_product_repository import (
    PostgresProductRepository,
)


async def main() -> None:
    settings = DatabaseSettings(postgres_db="shop_test_db")
    engine, session_factory = create_database(settings)

    async with session_factory() as session:
        database_name = await session.scalar(
            text("SELECT current_database()")
    )

    if database_name != "shop_test_db":
        await engine.dispose()
        raise RuntimeError("Integration tests require shop_test_db")

    repository = PostgresProductRepository(session_factory)

    request_key = RequestKey(f"test:{uuid4().hex}")

    product = Product(
        id=uuid4(),
        title="Test Product",
        image_sha256="a" * 64,
        request_key=request_key,
        created_at=datetime.now(timezone.utc),
    )

    try:
        saved = await repository.reserve(product)

        assert saved.id == product.id
        assert saved.status == ProductStatus.PENDING

        duplicate = await repository.reserve(
            replace(product, id=uuid4())
        )

        assert duplicate.id == saved.id

        image_key = ImageKey.for_product(saved.id)

        published = await repository.mark_ready(
            saved.id,
            image_key
        )

        assert published.status == ProductStatus.READY
        assert published.image_key == image_key

        repeated = await repository.mark_ready(
            saved.id,
            image_key
        )

        assert repeated.id == published.id
        assert repeated.image_key == image_key

        products = await repository.list_ready()

        assert any(item.id == saved.id for item in products)

        print("PostgreSQL repository OK")

    finally:
        try:
            async with session_factory.begin() as session:
                await session.execute(
                    delete(ProductORM).where(
                        ProductORM.request_key == request_key.value
                    )
                )
        finally:
            await engine.dispose()

class TestPostgresRepository(IsolatedAsyncioTestCase):

    async def test_product_lifecycle(self):
        await main()