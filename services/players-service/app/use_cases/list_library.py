"""Caso de uso: listar a biblioteca (jogos comprados) de um jogador."""
from __future__ import annotations

from app.domain.entities import LibraryEntry
from app.domain.repositories import LibraryRepository


class ListLibrary:
    def __init__(self, repository: LibraryRepository) -> None:
        self._repository = repository

    def execute(self, player_id: str) -> list[LibraryEntry]:
        return self._repository.list_by_player(player_id)
