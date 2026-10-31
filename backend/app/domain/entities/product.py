from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from uuid import UUID

class ProductStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"

@dataclass(frozen=True, slots=True)
class Product:
    id: UUID
    title: str
    image_sha256:str
    request_key:str
    created_at:datetime
    status: ProductStatus = ProductStatus.PENDING
    image_key: str | None = None

    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("Product title cannot be empty")

        if len(self.title.strip()) > 120:
            raise ValueError("Product title is too long")

        if not self.request_key.strip():
            raise ValueError("Request key cannot be empty")

        if self.status == ProductStatus.READY and (not self.image_key or not self.image_key.strip()):
            raise ValueError("Ready product must have an image")

    def mark_ready(self, image_key: str) -> "Product":
        if not image_key or not image_key.strip():
            raise ValueError("Image key cannot be empty")

        if self.status == ProductStatus.READY:
            if self.image_key == image_key:
                return self   
            raise ValueError("Product is already published")

        return replace(self, status = ProductStatus.READY, image_key = image_key)