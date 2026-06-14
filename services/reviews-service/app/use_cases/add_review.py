"""Caso de uso: adicionar uma avaliação."""
from __future__ import annotations

from app.domain.entities import Review
from app.domain.repositories import ReviewRepository


class AddReview:
    def __init__(self, repository: ReviewRepository) -> None:
        self._repository = repository

    def execute(self, *, game_id: str, author: str, rating: int, comment: str = "") -> Review:
        review = Review.create(game_id, author, rating, comment)
        self._repository.save(review)
        return review
