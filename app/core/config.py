from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/bookings_db"
    )
    redis_url: str = Field(default="redis://localhost:6379")

    secret_key: SecretStr = Field(default=SecretStr("secret"))
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=15)
    refresh_token_expire_days: int = Field(default=7)
    dummy_hash: str = Field(
        default="$argon2id$v=19$m=65536,t=3,p=4$e0JyHxJ6a6+wtVXpPRgbTA$x1TKqJ0PWOf7kKYLRIRwEgyyjj2bHSUGhXhMfyZY5Vk"
    )

    superuser_email: str = Field(default="admin@example.com")
    superuser_password: SecretStr = Field(default=SecretStr("admin1619"))

    mail_username: str = Field(default="user")
    mail_server: str = Field(default="localhost")
    mail_password: SecretStr = Field(default=SecretStr("password"))

    mail_port: int = Field(default=1025)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
