from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from uuid import uuid4

from app.domain.value_objects.request_key import RequestKey
from app.application.ports.product_repository import ProductRepository
from app.application.ports.image_storage import ImageStorage
from app.domain.entities.product import Product, ProductStatus
from app.domain.value_objects.image_key import ImageKey

@dataclass(frozen=True, slots=True)
class CreateProductCommand:
    title: str
    image_bytes: bytes
    content_type: str
    request_key: RequestKey


class ProductConflictError(Exception):
    """Request key is already used for a different product."""


class CreateProductUseCase:

    def __init__(
        self,
        repository: ProductRepository,
        image_storage: ImageStorage
    ) -> None:
        self._repository = repository
        self._image_storage = image_storage

    async def execute(
        self,
        command: CreateProductCommand
    ) -> Product:

        if command.content_type != "image/jpeg":
            raise ValueError("Only JPEG images are supported")

        if (
            not command.image_bytes
            or len(command.image_bytes) > 5 * 1024 * 1024
        ):
            raise ValueError("Invalid image size")

        if not command.image_bytes.startswith(b"\xff\xd8\xff"):
            raise ValueError("Invalid JPEG signature")

        image_hash = sha256(command.image_bytes).hexdigest()

        candidate = Product(
            id=uuid4(),
            title=command.title.strip(),
            image_sha256=image_hash,
            request_key=command.request_key,
            created_at=datetime.now(timezone.utc)
        )

        product = await self._repository.reserve(candidate)

        if (
            product.title != candidate.title
            or product.image_sha256 != candidate.image_sha256
        ):
            raise ProductConflictError(
                "Request key already belongs to another product"
            )

        if product.status == ProductStatus.READY:
            return product

        image_key = ImageKey.for_product(product.id)

        await self._image_storage.upload(
            key=image_key,
            content=command.image_bytes,
            content_type=command.content_type
        )

        return await self._repository.mark_ready(
            product_id=product.id,
            image_key=image_key
        )
