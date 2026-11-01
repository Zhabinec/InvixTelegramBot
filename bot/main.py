import asyncio

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BotSettings


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        "Invix Bot Shop starting"
    )


async def main() -> None:
    settings = BotSettings()

    bot = Bot(
        token=settings.bot_token.get_secret_value()
    )

    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
