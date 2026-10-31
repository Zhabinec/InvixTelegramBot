
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ImageKey:
    value: str

    def __post_init__(self) -> None:
        prefix = "products/"
        suffix = ".jpg"

        if not isinstance(self.value, str):
            raise ValueError("Image key must be a string")

        if not self.value.startswith(prefix) or not self.value.endswith(suffix):
            raise ValueError("Invalid image key format")

        raw_id = self.value[len(prefix):-len(suffix)]

        try:
            product_id = UUID(raw_id)
        except ValueError as exc:
            raise ValueError("Image key must contain a valid UUID") from exc

        if str(product_id) != raw_id:
            raise ValueError("Image key must contain a canonical UUID")

    @classmethod
    def for_product(cls, product_id: UUID) -> "ImageKey":
        return cls(f"products/{product_id}.jpg")
