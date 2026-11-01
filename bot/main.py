
import asyncio

import httpx
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

from config import BotSettings
from filters.admin import AdminFilter
from handlers.products import build_products_router


async def main() -> None:
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

    async with httpx.AsyncClient(
        base_url=settings.backend_url,
        timeout=30.0,
    ) as api_client:
        dispatcher.include_router(
            build_products_router(settings, api_client)
        )

        await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
