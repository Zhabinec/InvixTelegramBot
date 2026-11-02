
import asyncio
import time
from io import BytesIO
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from aiogram import Bot, Dispatcher
from aiogram.types import Message

from config import BotSettings
from handlers.products import build_products_router


@pytest.mark.asyncio
async def test_duplicate_update_uses_same_request_key() -> None:
    settings = BotSettings(
        _env_file=None,
        bot_token="123456:TEST",
        admin_api_token="test-admin-token",
        telegram_admin_id=42,
        mini_app_url="https://example.com",
        webhook_secret="test-webhook-secret",
    )

    request_keys: list[str] = []

    def handle_request(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/products"

        request_keys.append(request.headers["X-Request-Key"])

        return httpx.Response(
            201,
            json={"title": "Test Product"},
        )

    async def fake_download(
        self: Bot,
        file: object,
        destination: BytesIO,
    ) -> BytesIO:
        destination.write(b"\xff\xd8\xfftest-image")
        return destination

    update = {
        "update_id": 100,
        "message": {
            "message_id": 200,
            "date": int(time.time()),
            "chat": {"id": 42, "type": "private"},
            "from": {
                "id": 42,
                "is_bot": False,
                "first_name": "Admin",
            },
            "photo": [
                {
                    "file_id": "test-photo",
                    "file_unique_id": "unique-photo",
                    "width": 100,
                    "height": 100,
                }
            ],
            "caption": "Test Product",
        },
    }

    async with httpx.AsyncClient(
        base_url="http://backend",
        transport=httpx.MockTransport(handle_request),
    ) as api_client:
        dispatcher1 = Dispatcher()
        dispatcher2 = Dispatcher()

        dispatcher1.include_router(
            build_products_router(settings, api_client)
        )
        dispatcher2.include_router(
            build_products_router(settings, api_client)
        )

        async with (
            Bot(token="123456:TEST") as bot1,
            Bot(token="123456:TEST") as bot2,
        ):
            with (
                patch.object(Bot, "download", new=fake_download),
                patch.object(
                    Message,
                    "answer",
                    new_callable=AsyncMock,
                ) as answer_mock,
            ):
                await asyncio.gather(
                    dispatcher1.feed_raw_update(bot1, update),
                    dispatcher2.feed_raw_update(bot2, update),
                )

                assert answer_mock.await_count == 2

    assert request_keys == [
        "tg:42:200",
        "tg:42:200",
    ]
