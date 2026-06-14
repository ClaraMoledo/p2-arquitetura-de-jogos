"""Configuração lida do ambiente (12-factor)."""
from __future__ import annotations

import os


class Settings:
    def __init__(self) -> None:
        self.database_url: str = os.getenv("DATABASE_URL", "")
        self.port: int = int(os.getenv("PORT", "8001"))
        self.env: str = os.getenv("APP_ENV", "development")


settings = Settings()
