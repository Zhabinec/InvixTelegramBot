
import asyncio
from pathlib import Path
from uuid import uuid4

import httpx
import pytest

from app.infrastructure.config import ApiSettings


@pytest.mark.asyncio
async def test_concurrent_product_creation() -> None:
    image_path = (
        Path(__file__).resolve().parents[1]
        / "fixtures"
        / "product.jpg"
    )

    image_bytes = image_path.read_bytes()
    request_key = f"test-concurrent-{uuid4()}"
    token = ApiSettings().admin_api_token.get_secret_value()

    async with httpx.AsyncClient(
        base_url="http://127.0.0.1:18081/api/backend",
        timeout=60.0,
    ) as client:

        async def create_product() -> httpx.Response:
            return await client.post(
                "/products",
                headers={
                    "X-Admin-Token": token,
                    "X-Request-Key": request_key,
                },
                data={
                    "title": "Concurrent Test Product",
                },
                files={
                    "image": (
                        "product.jpg",
                        image_bytes,
                        "image/jpeg",
                    ),
                },
            )

        responses = await asyncio.gather(
            *(create_product() for _ in range(6))
        )

        assert all(
            response.status_code == 201
            for response in responses
        ), [
            (response.status_code, response.text)
            for response in responses
        ]

        product_ids = {
            response.json()["id"]
            for response in responses
        }

        assert len(product_ids) == 1

        catalog_response = await client.get("/products")
        catalog_response.raise_for_status()

        product_id = next(iter(product_ids))

        matching_products = [
            product
            for product in catalog_response.json()
            if product["id"] == product_id
        ]

        assert len(matching_products) == 1
        conflict_response = await client.post(
            "/products",
            headers={
                "X-Admin-Token": token,
                "X-Request-Key": request_key,
            },
            data={
                "title": "Different Product",
            },
            files={
                "image": (
                    "product.jpg",
                    image_bytes,
                    "image/jpeg",
                ),
            },
        )

        assert conflict_response.status_code == 409