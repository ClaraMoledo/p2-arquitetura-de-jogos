"""Rotas HTTP do catálogo (adaptadores de entrada)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.domain.entities import Game
from app.use_cases.create_game import CreateGame
from app.use_cases.list_games import ListGames

from .dependencies import provide_create_game, provide_list_games
from .schemas import GameIn

router = APIRouter()


def _to_dict(game: Game) -> dict:
    return {
        "id": game.id,
        "title": game.title,
        "genre": game.genre,
        "platform": game.platform,
        "priceCents": game.price_cents,
        "releaseYear": game.release_year,
        "available": game.available,
    }


@router.get("/games")
def list_games(use_case: ListGames = Depends(provide_list_games)) -> dict:
    games = use_case.execute()
    return {"data": [_to_dict(game) for game in games]}


@router.post("/games", status_code=status.HTTP_201_CREATED)
def create_game(payload: GameIn, use_case: CreateGame = Depends(provide_create_game)) -> dict:
    game = use_case.execute(
        title=payload.title,
        genre=payload.genre or "",
        platform=payload.platform or "",
        price_cents=payload.priceCents,
        release_year=payload.releaseYear,
    )
    return {"data": _to_dict(game)}
