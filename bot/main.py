import httpx

from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)

from config import BotSettings
from filters.admin import AdminFilter
from handlers.products import build_products_router


def create_app() -> web.Application:
    settings = BotSettings()

    bot = Bot(token=settings.bot_token.get_secret_value())
    dispatcher = Dispatcher()
    router = Router()

    catalog_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть каталог",
                    web_app=WebAppInfo(url=settings.mini_app_url),
                )
            ]
        ]
    )

    @router.message(CommandStart())
    async def start_handler(message: Message) -> None:
        await message.answer(
            "У меня есть товар",
            reply_markup=catalog_keyboard,
        )

    @router.message(
        Command("create_product"),
        AdminFilter(settings.telegram_admin_id),
    )
    async def create_product_handler(message: Message) -> None:
        await message.answer(
            "Отправь фотографию товара с названием "
            "в подписи одним сообщением."
        )

    @router.message(F.text)
    async def text_handler(message: Message) -> None:
        await message.answer(
            "У меня есть товар",
            reply_markup=catalog_keyboard,
        )

    dispatcher.include_router(router)

    api_client = httpx.AsyncClient(
        base_url=settings.backend_url,
        timeout=30.0,
    )

    dispatcher.include_router(
        build_products_router(settings, api_client)
    )

    app = web.Application()

    async def health(request: web.Request) -> web.Response:
        return web.json_response({"status": "ok"})

    app.router.add_get("/health", health)

    SimpleRequestHandler(
        dispatcher=dispatcher,
        bot=bot,
        secret_token=settings.webhook_secret.get_secret_value(),
        handle_in_background=False,
    ).register(app, path="/telegram/webhook")

    setup_application(app, dispatcher, bot=bot)

    async def close_api_client(app: web.Application) -> None:
        await api_client.aclose()

    app.on_cleanup.append(close_api_client)

    return app


if __name__ == "__main__":
    web.run_app(
        create_app(),
        host="0.0.0.0",
        port=8081,
    )
