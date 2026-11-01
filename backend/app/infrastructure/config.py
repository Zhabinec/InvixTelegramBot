
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_PATH = Path(__file__).resolve().parents[3] / ".env"


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    postgres_user: str
    postgres_password: SecretStr
    postgres_db: str
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5433


class MinioSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    minio_root_user: str
    minio_root_password: SecretStr
    minio_endpoint: str = "127.0.0.1:9000"
    minio_bucket: str = "products"
    minio_secure: bool = False


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    admin_api_token: SecretStr
