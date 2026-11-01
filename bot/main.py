import asyncio

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BotSettings


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

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
