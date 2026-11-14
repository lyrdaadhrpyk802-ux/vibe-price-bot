from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str = ""
    cache_ttl_seconds: int = 1200
    http_timeout_seconds: int = 20
    log_level: str = "INFO"


settings = Settings()
