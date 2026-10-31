from typing import Protocol
from uuid import UUID

from app.domain.entities.product import Product


class ProductRepository(Protocol):

    async def reserve(self, product: Product) -> Product:
        """Reserve a product or return an existing one."""
        ...

    async def mark_ready(
        self,
        product_id: UUID,
        image_key: str
    ) -> Product:
        """Publish a product after its image is uploaded."""
        ...

    async def list_ready(self) -> list[Product]:
        """Return published products."""
        ...