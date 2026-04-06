from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr


class Settings(BaseSettings):
    database_url: str = Field(default=...)
    redis_url: str = Field(default=...)
    
    secret_key: str = Field(default=...)
    algorithm: str = Field(default=...)
    access_token_expire_minutes: int = Field(default=...)
    refresh_token_expire_days: int = Field(default=...)
    dummy_hash: str = Field(default=...)

    superuser_email: str = Field(default=...)
    superuser_password: str = Field(default=...)

    mail_username: str = Field(default=...)
    mail_server: str = Field(default=...)
    mail_password: SecretStr = Field(default=...)
    mail_port: int = Field(default=...)

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()