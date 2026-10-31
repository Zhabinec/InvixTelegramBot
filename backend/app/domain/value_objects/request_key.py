
import re

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RequestKey:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise ValueError("Request key must be a string")

        if not re.fullmatch(r"[a-zA-Z0-9:_-]{1,160}", self.value):
            raise ValueError("Invalid request key format")
