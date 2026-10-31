
from app.domain.entities.product import Product
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.request_key import RequestKey
from app.infrastructure.database.models.product import ProductORM


class ProductMapper:

    @staticmethod
    def to_domain(model: ProductORM) -> Product:
        return Product(
            id=model.id,
            title=model.title,
            image_sha256=model.image_sha256,
            request_key=RequestKey(model.request_key),
            created_at=model.created_at,
            status=model.status,
            image_key=ImageKey(model.image_key)
            if model.image_key is not None else None
        )

    @staticmethod
    def to_orm(product: Product) -> ProductORM:
        return ProductORM(
            id=product.id,
            title=product.title,
            image_sha256=product.image_sha256,
            request_key=product.request_key.value,
            created_at=product.created_at,
            status=product.status,
            image_key=product.image_key.value
            if product.image_key is not None else None
        )
