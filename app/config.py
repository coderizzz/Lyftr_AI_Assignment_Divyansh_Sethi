import os
from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str
    webhook_secret: str
    log_level: str = "INFO"


def load_settings() -> Settings:
    database_url = os.getenv("DATABASE_URL")
    webhook_secret = os.getenv("WEBHOOK_SECRET")
    log_level = os.getenv("LOG_LEVEL", "INFO")

    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    if not webhook_secret:
        raise RuntimeError("WEBHOOK_SECRET is required")

    return Settings(
        database_url=database_url,
        webhook_secret=webhook_secret,
        log_level=log_level,
    )


settings = load_settings()
