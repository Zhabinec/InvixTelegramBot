
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime
