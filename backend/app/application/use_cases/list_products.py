
from app.application.ports.product_repository import ProductRepository
from app.domain.entities.product import Product


class ListProductsUseCase:

    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    async def execute(self) -> list[Product]:
        return await self._repository.list_ready()
