
import asyncio
from io import BytesIO

from minio import Minio
from datetime import timedelta

from app.domain.value_objects.image_key import ImageKey
from app.infrastructure.config import MinioSettings


class MinioImageStorage:
    def __init__(self, settings: MinioSettings) -> None:
        self._bucket = settings.minio_bucket

        self._client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password.get_secret_value(),
            secure=settings.minio_secure,
        )

    async def upload(
        self,
        key: ImageKey,
        content: bytes,
        content_type: str,
    ) -> None:
        await asyncio.to_thread(
            self._client.put_object,
            bucket_name=self._bucket,
            object_name=key.value,
            data=BytesIO(content),
            length=len(content),
            content_type=content_type,
        )

    
    async def get_download_url(
        self,
        key: ImageKey,
    ) -> str:
        return await asyncio.to_thread(
            self._client.presigned_get_object,
            bucket_name=self._bucket,
            object_name=key.value,
            expires=timedelta(minutes=15),
        )
