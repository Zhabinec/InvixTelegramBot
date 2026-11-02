
import asyncio

from aiogram import Bot

from config import BotSettings


async def main() -> None:
    settings = BotSettings()

    webhook_url = (
        f"{settings.mini_app_url.rstrip('/')}/telegram/webhook"
    )

    async with Bot(
        token=settings.bot_token.get_secret_value()
    ) as bot:
        success = await bot.set_webhook(
            url=webhook_url,
            secret_token=settings.webhook_secret.get_secret_value(),
            allowed_updates=["message"],
            drop_pending_updates=False,
        )

        info = await bot.get_webhook_info()

        print(f"Webhook registered: {success}")
        print(f"Webhook URL: {info.url}")
        print(f"Pending updates: {info.pending_update_count}")

        if info.last_error_message:
            print(f"Last delivery error: {info.last_error_message}")


if __name__ == "__main__":
    asyncio.run(main())
