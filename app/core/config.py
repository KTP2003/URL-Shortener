from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    base_url: str
    redis_url: str
    cache_ttl: int = 3600

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        env_file_encoding_errors = "ignore"
    )

settings = Settings()