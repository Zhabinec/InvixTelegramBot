
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile, status

from app.application.ports.image_storage import ImageStorage
from app.application.use_cases.list_products import ListProductsUseCase
from app.presentation.api.dependencies import (
    get_image_storage,
    get_list_products_use_case,
)
from app.presentation.api.schemas.product import ProductResponse

from app.application.use_cases.create_product import (
    CreateProductCommand,
    CreateProductUseCase,
    ProductConflictError,
)
from app.domain.value_objects.request_key import RequestKey
from app.presentation.api.dependencies import (
    get_create_product_use_case,
    require_admin_token,
)

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
    image_storage: Annotated[
        ImageStorage,
        Depends(get_image_storage),
    ],
) -> list[ProductResponse]:
    products = await use_case.execute()
    result: list[ProductResponse] = []

    for product in products:
        if product.image_key is None:
            raise RuntimeError("Ready product has no image")

        image_url = await image_storage.get_download_url(
            product.image_key
        )

        result.append(
            ProductResponse(
                id=product.id,
                title=product.title,
                created_at=product.created_at,
                image_url=image_url,
            )
        )

    return result


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_token)],
)
async def create_product(
    use_case: Annotated[
        CreateProductUseCase,
        Depends(get_create_product_use_case),
    ],
    image_storage: Annotated[
        ImageStorage,
        Depends(get_image_storage),
    ],
    request_key: Annotated[
        str,
        Header(alias="X-Request-Key"),
    ],
    title: Annotated[
        str,
        Form(min_length=1, max_length=120),
    ],
    image: Annotated[
        UploadFile,
        File(),
    ],
) -> ProductResponse:
    try:
        image_bytes = await image.read(5 * 1024 * 1024 + 1)

        command = CreateProductCommand(
            title=title,
            image_bytes=image_bytes,
            content_type=image.content_type or "",
            request_key=RequestKey(request_key),
        )

        product = await use_case.execute(command)

    except ProductConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail="Request key already used for another product",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    finally:
        await image.close()

    if product.image_key is None:
        raise RuntimeError("Created product has no image")

    image_url = await image_storage.get_download_url(
        product.image_key
    )

    return ProductResponse(
        id=product.id,
        title=product.title,
        created_at=product.created_at,
        image_url=image_url,
    )
