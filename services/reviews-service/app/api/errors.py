"""Tratadores de erro: respostas amigáveis, sem detalhe técnico."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.exceptions import DatabaseUnavailable, DomainError

_DB_DOWN_MESSAGE = "As avaliações estão indisponíveis no momento. Tente novamente em instantes."


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def _handle_domain(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": {"code": "VALIDACAO", "message": str(exc)}},
        )

    @app.exception_handler(DatabaseUnavailable)
    async def _handle_db(_: Request, __: DatabaseUnavailable) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={"error": {"code": "SERVICO_INDISPONIVEL", "message": _DB_DOWN_MESSAGE}},
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_validation(_: Request, __: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDACAO",
                    "message": "Dados inválidos. Confira os campos e tente novamente.",
                }
            },
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
        print(f"[reviews-service] erro inesperado: {type(exc).__name__}: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "ERRO_INTERNO",
                    "message": "Algo deu errado por aqui. Tente novamente em instantes.",
                }
            },
        )
