"""Ponto de entrada do reviews-service (FastAPI)."""
from __future__ import annotations

import threading
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.errors import register_error_handlers
from app.api.routes import router
from app.infra.settings import settings


def _init_db_with_retry() -> None:
    """Prepara o schema em segundo plano; se o banco estiver fora, segue tentando."""
    from app.infra.database import get_engine
    from app.infra.models import Base
    from app.infra.seed import seed

    attempt = 1
    while True:
        try:
            Base.metadata.create_all(get_engine())
            seed()
            print("[reviews-service] schema de avaliações pronto.")
            return
        except Exception as exc:
            # Captura ampla intencional: a migração nunca pode derrubar o serviço.
            wait = min(30, attempt * 3)
            print(f"[reviews-service] banco indisponível (tentativa {attempt}): {exc}. Retry em {wait}s.")
            time.sleep(wait)
            attempt += 1


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.database_url:
        threading.Thread(target=_init_db_with_retry, daemon=True).start()
    yield


def _database_status() -> str:
    if not settings.database_url:
        return "not-configured"
    try:
        from sqlalchemy import text

        from app.infra.database import get_engine

        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return "up"
    except Exception:
        return "down"


def create_app() -> FastAPI:
    app = FastAPI(title="Ludoteca — Avaliações", lifespan=lifespan)
    register_error_handlers(app)
    app.include_router(router)

    @app.get("/health")
    def health() -> dict:
        return {"service": "reviews-service", "status": "ok", "database": _database_status()}

    return app


app = create_app()
