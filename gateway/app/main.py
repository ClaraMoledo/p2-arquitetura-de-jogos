"""Ponto de entrada do gateway (BFF) da Ludoteca."""
from __future__ import annotations

from fastapi import FastAPI

from app.api.errors import register_error_handlers
from app.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(title="Ludoteca — Gateway")
    register_error_handlers(app)
    app.include_router(router)
    return app


app = create_app()
