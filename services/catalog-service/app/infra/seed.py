"""Popular o catálogo com jogos de demonstração (idempotente)."""
from __future__ import annotations

from .database import get_session_factory
from .models import GameModel

_SEED = [
    dict(id="a1000000-0000-0000-0000-000000000001", title="Aurora Frontier",
         genre="RPG de Aventura", platform="PC / Console", price_cents=19900, release_year=2023, available=True),
    dict(id="a1000000-0000-0000-0000-000000000002", title="Neon Circuit",
         genre="Corrida Futurista", platform="PC", price_cents=12900, release_year=2022, available=True),
    dict(id="a1000000-0000-0000-0000-000000000003", title="Mistveil Chronicles",
         genre="Estratégia", platform="PC / Console", price_cents=15900, release_year=2024, available=True),
    dict(id="a1000000-0000-0000-0000-000000000004", title="Pixel Raiders",
         genre="Plataforma", platform="Mobile / PC", price_cents=4900, release_year=2021, available=True),
    dict(id="a1000000-0000-0000-0000-000000000005", title="Stellar Drift",
         genre="Simulação Espacial", platform="PC", price_cents=17900, release_year=2024, available=True),
]


def seed() -> None:
    session_factory = get_session_factory()
    with session_factory() as session:
        if session.query(GameModel).count() > 0:
            return
        session.add_all(GameModel(**row) for row in _SEED)
        session.commit()
