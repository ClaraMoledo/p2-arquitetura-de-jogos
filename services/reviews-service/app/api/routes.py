"""Rotas HTTP das avaliações."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.domain.entities import Review
from app.use_cases.add_review import AddReview
from app.use_cases.compute_averages import ComputeAverages
from app.use_cases.list_reviews import ListReviews

from .dependencies import provide_add_review, provide_compute_averages, provide_list_reviews
from .schemas import ReviewIn

router = APIRouter()


def _to_dict(review: Review) -> dict:
    return {
        "id": review.id,
        "gameId": review.game_id,
        "author": review.author,
        "rating": review.rating,
        "comment": review.comment,
        "createdAt": review.created_at,
    }


@router.get("/reviews")
def list_reviews(
    gameId: str | None = None,
    use_case: ListReviews = Depends(provide_list_reviews),
) -> dict:
    reviews = use_case.execute(gameId)
    return {"data": [_to_dict(review) for review in reviews]}


@router.post("/reviews", status_code=status.HTTP_201_CREATED)
def add_review(payload: ReviewIn, use_case: AddReview = Depends(provide_add_review)) -> dict:
    review = use_case.execute(
        game_id=payload.gameId,
        author=payload.author,
        rating=payload.rating,
        comment=payload.comment or "",
    )
    return {"data": _to_dict(review)}


@router.get("/averages")
def averages(use_case: ComputeAverages = Depends(provide_compute_averages)) -> dict:
    return {"data": use_case.execute()}
