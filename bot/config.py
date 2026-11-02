from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: SecretStr
    admin_api_token: SecretStr
    backend_url: str = "http://127.0.0.1:8000"
    telegram_admin_id: int
    mini_app_url: str
    webhook_secret: SecretStr