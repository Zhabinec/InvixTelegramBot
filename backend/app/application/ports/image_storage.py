from typing import Protocol
from app.domain.value_objects.image_key import ImageKey
from datetime import timedelta


class ImageStorage(Protocol):

    async def upload(self,key: ImageKey,content: bytes,content_type: str) -> None:
        """Upload an image to object storage."""
        ...

    async def get_download_url(self, key: ImageKey) -> str:
        ...

    