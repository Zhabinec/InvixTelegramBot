
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities.product import ProductStatus
from app.infrastructure.database.base import Base


class ProductORM(Base):
    __tablename__ = "products"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    image_sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )

    request_key: Mapped[str] = mapped_column(
        String(160),
        unique=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    status: Mapped[ProductStatus] = mapped_column(
        Enum(
            ProductStatus,
            name="product_status",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda statuses: [
                status.value for status in statuses
            ]
        ),
        nullable=False
    )

    image_key: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True
    )
