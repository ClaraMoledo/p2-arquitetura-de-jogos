"""Provedores de dependência (injeção via FastAPI Depends)."""
from __future__ import annotations

from app.infra.factory import create_game_repository
from app.use_cases.create_game import CreateGame
from app.use_cases.list_games import ListGames


def provide_create_game() -> CreateGame:
    return CreateGame(create_game_repository())


def provide_list_games() -> ListGames:
    return ListGames(create_game_repository())
