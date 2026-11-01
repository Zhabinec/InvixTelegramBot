
from typing import Annotated

from fastapi import Depends, Request

from app.application.use_cases.create_product import CreateProductUseCase
from app.application.use_cases.list_products import ListProductsUseCase
from app.infrastructure.repositories.postgres_product_repository import (
    PostgresProductRepository,
)


def get_product_repository(request: Request) -> PostgresProductRepository:
    return PostgresProductRepository(
        request.app.state.session_factory
    )


def get_create_product_use_case(
    request: Request,
    repository: Annotated[
        PostgresProductRepository,
        Depends(get_product_repository),
    ],
) -> CreateProductUseCase:
    return CreateProductUseCase(
        repository,
        request.app.state.image_storage,
    )


def get_list_products_use_case(
    repository: Annotated[
        PostgresProductRepository,
        Depends(get_product_repository),
    ],
) -> ListProductsUseCase:
    return ListProductsUseCase(repository)
