
from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.use_cases.list_products import ListProductsUseCase
from app.presentation.api.dependencies import get_list_products_use_case
from app.presentation.api.schemas.product import ProductResponse


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.get("", response_model=list[ProductResponse])
async def list_products(
    use_case: Annotated[
        ListProductsUseCase,
        Depends(get_list_products_use_case),
    ],
) -> list[ProductResponse]:
    products = await use_case.execute()

    return [
        ProductResponse(
            id=product.id,
            title=product.title,
            created_at=product.created_at,
        )
        for product in products
    ]
