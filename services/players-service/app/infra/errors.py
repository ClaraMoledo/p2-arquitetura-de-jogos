"""Detecção de erros de conexão com o banco."""
from __future__ import annotations

from sqlalchemy.exc import DBAPIError, InterfaceError, OperationalError


def is_connection_error(exc: Exception) -> bool:
    """Indica se o erro é de indisponibilidade de conexão (banco fora do ar)."""
    if isinstance(exc, (OperationalError, InterfaceError)):
        return True
    if isinstance(exc, DBAPIError) and exc.connection_invalidated:
        return True
    return False
