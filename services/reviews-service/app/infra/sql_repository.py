"""Implementação do repositório de avaliações com SQLAlchemy."""
from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError

from app.domain.entities import Review
from app.domain.exceptions import DatabaseUnavailable

from .database import get_session_factory
from .errors import is_connection_error
from .models import ReviewModel


class SqlReviewRepository:
    def save(self, review: Review) -> None:
        session_factory = get_session_factory()
        try:
            with session_factory() as session:
                session.merge(
                    ReviewModel(
                        id=review.id,
                        game_id=review.game_id,
                        author=review.author,
                        rating=review.rating,
                        comment=review.comment,
                        created_at=review.created_at,
                    )
                )
                session.commit()
        except SQLAlchemyError as exc:
            raise self._translate(exc) from exc

    def list_by_game(self, game_id: str) -> list[Review]:
        session_factory = get_session_factory()
        try:
            with session_factory() as session:
                rows = (
                    session.query(ReviewModel)
                    .filter(ReviewModel.game_id == game_id)
                    .order_by(ReviewModel.created_at.desc())
                    .all()
                )
                return [self._to_entity(row) for row in rows]
        except SQLAlchemyError as exc:
            raise self._translate(exc) from exc

    def list_all(self) -> list[Review]:
        session_factory = get_session_factory()
        try:
            with session_factory() as session:
                rows = session.query(ReviewModel).order_by(ReviewModel.created_at.desc()).all()
                return [self._to_entity(row) for row in rows]
        except SQLAlchemyError as exc:
            raise self._translate(exc) from exc

    @staticmethod
    def _to_entity(row: ReviewModel) -> Review:
        return Review.restore(
            id=row.id,
            game_id=row.game_id,
            author=row.author,
            rating=row.rating,
            comment=row.comment,
            created_at=row.created_at,
        )

    @staticmethod
    def _translate(exc: SQLAlchemyError) -> Exception:
        if is_connection_error(exc):
            return DatabaseUnavailable()
        return exc
