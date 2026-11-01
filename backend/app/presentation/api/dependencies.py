
from typing import Annotated

from fastapi import Depends, Request

from app.application.ports.image_storage import ImageStorage
from app.application.use_cases.create_product import CreateProductUseCase
from app.application.use_cases.list_products import ListProductsUseCase
from app.infrastructure.repositories.postgres_product_repository import (
    PostgresProductRepository,
)

from hmac import compare_digest
from fastapi import Header, HTTPException
from app.infrastructure.config import ApiSettings

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

def get_image_storage(request: Request) -> ImageStorage:
    return request.app.state.image_storage


def require_admin_token(
    token: Annotated[
        str | None,
        Header(alias="X-Admin-Token"),
    ] = None,
) -> None:
    expected_token = ApiSettings().admin_api_token.get_secret_value()

    if token is None or not compare_digest(token, expected_token):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )
