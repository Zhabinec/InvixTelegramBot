from typing import Protocol
from app.domain.value_objects.image_key import ImageKey


class ImageStorage(Protocol):

    async def upload(self,key: ImageKey,content: bytes,content_type: str) -> None:
        """Upload an image to object storage."""
        ...