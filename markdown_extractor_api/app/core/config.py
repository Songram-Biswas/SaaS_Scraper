from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Markdown Extractor API"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/extractor_saas"
    PADDLE_WEBHOOK_SECRET: str = "paddle_secret_placeholder"
    API_ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()