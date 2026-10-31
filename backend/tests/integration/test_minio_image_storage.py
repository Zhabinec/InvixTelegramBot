
import asyncio
from unittest import IsolatedAsyncioTestCase
from uuid import uuid4

from minio import Minio

from app.domain.value_objects.image_key import ImageKey
from app.infrastructure.config import MinioSettings
from app.infrastructure.storage.minio_image_storage import MinioImageStorage


class TestMinioImageStorage(IsolatedAsyncioTestCase):
    async def test_upload(self) -> None:
        settings = MinioSettings()
        storage = MinioImageStorage(settings)

        client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password.get_secret_value(),
            secure=settings.minio_secure,
        )

        key = ImageKey.for_product(uuid4())
        content = b"test-image-content"
        uploaded = False

        try:
            await storage.upload(
                key=key,
                content=content,
                content_type="image/jpeg",
            )
            uploaded = True

            metadata = await asyncio.to_thread(
                client.stat_object,
                settings.minio_bucket,
                key.value,
            )

            self.assertEqual(metadata.size, len(content))
            self.assertEqual(metadata.content_type, "image/jpeg")

        finally:
            if uploaded:
                await asyncio.to_thread(
                    client.remove_object,
                    settings.minio_bucket,
                    key.value,
                )
