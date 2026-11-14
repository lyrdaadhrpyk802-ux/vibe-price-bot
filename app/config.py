from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    bot_token: str = Field(default="", validation_alias="VIBE_BOT_TOKEN")
    cache_ttl_seconds: int = 1200
    http_timeout_seconds: int = 20
    log_level: str = "INFO"

settings = Settings()
