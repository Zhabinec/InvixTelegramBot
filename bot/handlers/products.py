
from io import BytesIO

import httpx
from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message

from config import BotSettings
from filters.admin import AdminFilter


def build_products_router(
    settings: BotSettings,
    api_client: httpx.AsyncClient,
) -> Router:
    router = Router()

    @router.message(F.photo, AdminFilter(settings.telegram_admin_id))
    async def add_product(message: Message, bot: Bot) -> None:
        title = (message.caption or "").strip()

        if not title or len(title) > 120:
            await message.answer(
                "Добавь к фотографии название товара до 120 символов."
            )
            return

        photos = message.photo

        if not photos:
            return

        photo = photos[-1]

        if photo.file_size is not None and photo.file_size > 5 * 1024 * 1024:
            await message.answer("Фотография слишком большая. Максимум 5 МБ.")
            return

        image_stream = BytesIO()

        try:
            await bot.download(photo, destination=image_stream)
        except TelegramAPIError:
            await message.answer("Не удалось скачать фотографию из Telegram.")
            return

        image_bytes = image_stream.getvalue()

        if not image_bytes or len(image_bytes) > 5 * 1024 * 1024:
            await message.answer("Некорректная фотография или размер больше 5 МБ.")
            return

        request_key = f"tg:{message.chat.id}:{message.message_id}"

        try:
            response = await api_client.post(
                "/products",
                headers={
                    "X-Admin-Token": settings.admin_api_token.get_secret_value(),
                    "X-Request-Key": request_key,
                },
                data={"title": title},
                files={
                    "image": ("product.jpg", image_bytes, "image/jpeg"),
                },
            )
        except httpx.RequestError:
            await message.answer("Не удалось связаться с сервером.")
            return

        if response.status_code == 201:
            product = response.json()
            await message.answer(
                f"Товар «{product['title']}» добавлен в каталог!"
            )
        elif response.status_code == 409:
            await message.answer("Конфликт при создании товара.")
        else:
            await message.answer(
                f"Не удалось создать товар. HTTP {response.status_code}"
            )

    return router
