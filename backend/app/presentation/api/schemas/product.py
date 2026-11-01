
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class ProductResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    image_url: HttpUrl