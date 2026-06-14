"""Configuração do gateway lida do ambiente."""
from __future__ import annotations

import os


class Settings:
    def __init__(self) -> None:
        self.port: int = int(os.getenv("PORT", "8000"))
        self.catalog_url: str = os.getenv("CATALOG_SERVICE_URL", "http://localhost:8001")
        self.reviews_url: str = os.getenv("REVIEWS_SERVICE_URL", "http://localhost:8002")
        self.players_url: str = os.getenv("PLAYERS_SERVICE_URL", "http://localhost:8003")


settings = Settings()
