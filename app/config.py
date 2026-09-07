

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GITHUB_TOKEN: str
    GITHUB_OWNER: str
    GITHUB_REPO: str
    WEBHOOK_SECRET: str
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()