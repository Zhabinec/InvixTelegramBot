
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.entities.product import Product, ProductStatus
from app.domain.value_objects.image_key import ImageKey
from app.infrastructure.database.models.product import ProductORM
from app.infrastructure.database.mappers.product_mapper import ProductMapper


class PostgresProductRepository:

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        self._session_factory = session_factory

    async def reserve(self, product: Product) -> Product:
        model = ProductMapper.to_orm(product)

        statement = (
            insert(ProductORM)
            .values(
                id=model.id,
                title=model.title,
                image_sha256=model.image_sha256,
                request_key=model.request_key,
                created_at=model.created_at,
                status=model.status,
                image_key=model.image_key,
            )
            .on_conflict_do_nothing(
                index_elements=[ProductORM.request_key]
            )
        )

        async with self._session_factory.begin() as session:
            await session.execute(statement)

            result = await session.scalar(
                select(ProductORM).where(
                    ProductORM.request_key == model.request_key
                )
            )

            if result is None:
                raise RuntimeError("Failed to reserve product")

            return ProductMapper.to_domain(result)
    
    async def mark_ready(
        self,
        product_id: UUID,
        image_key: ImageKey
    ) -> Product:

        if image_key != ImageKey.for_product(product_id):
            raise ValueError("Image key does not match product")

        statement = (
            update(ProductORM)
            .where(
                ProductORM.id == product_id,
                ProductORM.status == ProductStatus.PENDING
            )
            .values(
                status=ProductStatus.READY,
                image_key=image_key.value
            )
            .returning(ProductORM)
        )

        async with self._session_factory.begin() as session:
            model = await session.scalar(statement)

            if model is None:
                model = await session.scalar(
                    select(ProductORM).where(
                        ProductORM.id == product_id
                    )
                )

            if model is None:
                raise LookupError("Product not found")

            if (
                model.status != ProductStatus.READY
                or model.image_key != image_key.value
            ):
                raise ValueError("Product cannot be published")

            return ProductMapper.to_domain(model)

