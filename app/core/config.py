from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str # this is the database URL for connecting to the PostgreSQL database, and it is str cause it is a string value that represents the connection string for the database.
    base_url: str

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        env_file_encoding_errors = "ignore"
    )

settings = Settings()
#print(settings.database_url)