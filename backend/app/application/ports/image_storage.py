from typing import Protocol


class ImageStorage(Protocol):

    async def upload(self,key: str,content: bytes,content_type: str) -> None:
        """Upload an image to object storage."""
        ...