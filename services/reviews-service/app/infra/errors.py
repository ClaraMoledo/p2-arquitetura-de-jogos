"""Detecção de erros de conexão com o banco."""
from __future__ import annotations

from sqlalchemy.exc import DBAPIError, InterfaceError, OperationalError


def is_connection_error(exc: Exception) -> bool:
    if isinstance(exc, (OperationalError, InterfaceError)):
        return True
    if isinstance(exc, DBAPIError) and exc.connection_invalidated:
        return True
    return False
