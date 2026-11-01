import asyncio
import httpx

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BotSettings

from handlers.products import build_products_router

router = Router()



@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    if message.from_user is None:
        return

    await message.answer(
        f"Invix Bot Shop starting\n"
        f"Telegram ID: {message.from_user.id}"
    )



async def main() -> None:
    settings = BotSettings()

    bot = Bot(
        token=settings.bot_token.get_secret_value()
    )

    dispatcher = Dispatcher()
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
