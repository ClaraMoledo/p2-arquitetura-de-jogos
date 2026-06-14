"""Provedores de dependência (FastAPI Depends)."""
from __future__ import annotations

from app.infra.factory import create_review_repository
from app.use_cases.add_review import AddReview
from app.use_cases.compute_averages import ComputeAverages
from app.use_cases.list_reviews import ListReviews


def provide_add_review() -> AddReview:
    return AddReview(create_review_repository())


def provide_list_reviews() -> ListReviews:
    return ListReviews(create_review_repository())


def provide_compute_averages() -> ComputeAverages:
    return ComputeAverages(create_review_repository())
