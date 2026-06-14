"""Factories de repositório: SQLAlchemy quando há banco; memória caso contrário.

Cada factory devolve a abstração; o resto da aplicação não sabe qual
implementação está por trás (Inversão de Dependência).
"""
from __future__ import annotations

from app.domain.repositories import (
    FriendshipRepository,
    LibraryRepository,
    PlayerRepository,
    WishlistRepository,
)

from .memory import (
    InMemoryFriendshipRepository,
    InMemoryLibraryRepository,
    InMemoryPlayerRepository,
    InMemoryWishlistRepository,
)
from .settings import settings

# Em memória, os repositórios precisam ser singletons para compartilhar estado
# entre as requisições (sem banco, é o nosso "armazenamento").
_memory_players = InMemoryPlayerRepository()
_memory_library = InMemoryLibraryRepository()
_memory_wishlist = InMemoryWishlistRepository()
_memory_friendships = InMemoryFriendshipRepository()


def create_player_repository() -> PlayerRepository:
    if settings.database_url:
        from .sql_repository import SqlPlayerRepository

        return SqlPlayerRepository()
    return _memory_players


def create_library_repository() -> LibraryRepository:
    if settings.database_url:
        from .sql_repository import SqlLibraryRepository

        return SqlLibraryRepository()
    return _memory_library


def create_wishlist_repository() -> WishlistRepository:
    if settings.database_url:
        from .sql_repository import SqlWishlistRepository

        return SqlWishlistRepository()
    return _memory_wishlist


def create_friendship_repository() -> FriendshipRepository:
    if settings.database_url:
        from .sql_repository import SqlFriendshipRepository

        return SqlFriendshipRepository()
    return _memory_friendships
