"""Rede de segurança: qualquer erro vira resposta amigável."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def _handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
        print(f"[gateway] erro inesperado: {type(exc).__name__}: {exc}")
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "SERVICO_INDISPONIVEL",
                    "message": "Estamos com instabilidade no momento. Tente novamente em instantes.",
                }
            },
        )
