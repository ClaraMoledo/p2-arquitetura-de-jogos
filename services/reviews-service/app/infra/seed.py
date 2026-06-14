"""Popular avaliações de demonstração (idempotente)."""
from __future__ import annotations

from datetime import datetime, timezone

from .database import get_session_factory
from .models import ReviewModel

_NOW = datetime.now(timezone.utc).isoformat()

# Avaliações ligadas aos jogos semeados no catalog-service.
_SEED = [
    dict(id="b2000000-0000-0000-0000-000000000001", game_id="a1000000-0000-0000-0000-000000000001",
         author="Marina", rating=5, comment="História incrível e mundo aberto enorme.", created_at=_NOW),
    dict(id="b2000000-0000-0000-0000-000000000002", game_id="a1000000-0000-0000-0000-000000000001",
         author="Rafael", rating=4, comment="Muito bom, mas pesado em PCs antigos.", created_at=_NOW),
    dict(id="b2000000-0000-0000-0000-000000000003", game_id="a1000000-0000-0000-0000-000000000002",
         author="Bruno", rating=3, comment="Divertido, porém repetitivo.", created_at=_NOW),
    dict(id="b2000000-0000-0000-0000-000000000004", game_id="a1000000-0000-0000-0000-000000000003",
         author="Carla", rating=5, comment="Melhor jogo de estratégia do ano!", created_at=_NOW),
    dict(id="b2000000-0000-0000-0000-000000000005", game_id="a1000000-0000-0000-0000-000000000005",
         author="Diego", rating=4, comment="Simulação relaxante e bonita.", created_at=_NOW),
]


def seed() -> None:
    session_factory = get_session_factory()
    with session_factory() as session:
        if session.query(ReviewModel).count() > 0:
            return
        session.add_all(ReviewModel(**row) for row in _SEED)
        session.commit()
