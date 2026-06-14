"""Implementação do repositório com SQLAlchemy."""
from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError

from app.domain.entities import Game
from app.domain.exceptions import DatabaseUnavailable

from .database import get_session_factory
from .errors import is_connection_error
from .models import GameModel


class SqlGameRepository:
    """Adaptador de saída: traduz erros de conexão em DatabaseUnavailable."""

    def save(self, game: Game) -> None:
        session_factory = get_session_factory()
        try:
            with session_factory() as session:
                session.merge(
                    GameModel(
                        id=game.id,
                        title=game.title,
                        genre=game.genre,
                        platform=game.platform,
                        price_cents=game.price_cents,
                        release_year=game.release_year,
                        available=game.available,
                    )
                )
                session.commit()
        except SQLAlchemyError as exc:
            raise self._translate(exc) from exc

    def list_all(self) -> list[Game]:
        session_factory = get_session_factory()
        try:
            with session_factory() as session:
                rows = session.query(GameModel).order_by(GameModel.title).all()
                return [self._to_entity(row) for row in rows]
        except SQLAlchemyError as exc:
            raise self._translate(exc) from exc

    @staticmethod
    def _to_entity(row: GameModel) -> Game:
        return Game.restore(
            id=row.id,
            title=row.title,
            genre=row.genre,
            platform=row.platform,
            price_cents=row.price_cents,
            release_year=row.release_year,
            available=row.available,
        )

    @staticmethod
    def _translate(exc: SQLAlchemyError) -> Exception:
        if is_connection_error(exc):
            return DatabaseUnavailable()
        return exc
