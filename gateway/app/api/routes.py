"""Rotas do gateway: roteamento, agregação de ranking e resiliência."""
from __future__ import annotations

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from app.config import settings
from app.infra.service_client import ServiceClient
from app.ranking.factory import create_ranking_strategy

router = APIRouter()

catalog = ServiceClient(settings.catalog_url, "catalog-service")
reviews = ServiceClient(settings.reviews_url, "reviews-service")
players = ServiceClient(settings.players_url, "players-service")

_CATALOG_DOWN = "O catálogo está indisponível no momento. Tente novamente em instantes."
_REVIEWS_DOWN = "As avaliações estão indisponíveis no momento. Tente novamente em instantes."
_PLAYERS_DOWN = "Os perfis estão indisponíveis no momento. Tente novamente em instantes."


def _unavailable(message: str) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"error": {"code": "SERVICO_INDISPONIVEL", "message": message}},
    )


def _forward(result: dict) -> JSONResponse:
    return JSONResponse(status_code=result["status"], content=result["data"])


def _extract_list(result: dict) -> list:
    data = result.get("data")
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        return data["data"]
    return []


@router.get("/api/games")
def list_games() -> JSONResponse:
    try:
        return _forward(catalog.get("/games"))
    except Exception:
        return _unavailable(_CATALOG_DOWN)


@router.post("/api/games")
def create_game(payload: dict = Body(...)) -> JSONResponse:
    try:
        return _forward(catalog.post("/games", json=payload))
    except Exception:
        return _unavailable("Não foi possível salvar o jogo agora. Tente novamente em instantes.")


@router.get("/api/games/{game_id}/reviews")
def game_reviews(game_id: str) -> JSONResponse:
    try:
        return _forward(reviews.get("/reviews", params={"gameId": game_id}))
    except Exception:
        return _unavailable(_REVIEWS_DOWN)


@router.post("/api/games/{game_id}/reviews")
def add_review(game_id: str, payload: dict = Body(...)) -> JSONResponse:
    body = {**payload, "gameId": game_id}
    try:
        return _forward(reviews.post("/reviews", json=body))
    except Exception:
        return _unavailable("Não foi possível registrar a avaliação agora. Tente novamente em instantes.")


@router.get("/api/ranking")
def ranking(by: str | None = None):
    # O catálogo é obrigatório para montar o ranking.
    try:
        games = _extract_list(catalog.get("/games"))
    except Exception:
        return _unavailable(_CATALOG_DOWN)

    # As avaliações são opcionais: se estiverem fora, o ranking sai sem
    # notas (degradação parcial), em vez de falhar por completo.
    averages_by_game: dict[str, dict] = {}
    reviews_available = True
    try:
        for item in _extract_list(reviews.get("/averages")):
            averages_by_game[item["gameId"]] = item
    except Exception:
        reviews_available = False

    enriched = []
    for game in games:
        average = averages_by_game.get(game.get("id"))
        enriched.append(
            {
                **game,
                "average": average["average"] if average else None,
                "reviewCount": average["count"] if average else 0,
            }
        )

    strategy = create_ranking_strategy(by)
    ordered = strategy.order(enriched)
    return {
        "data": {
            "ranking": ordered,
            "orderedBy": strategy.name,
            "reviewsAvailable": reviews_available,
        }
    }


# ---------------------------------------------------------------------------
# Jogadores, loja, biblioteca, lista de desejos e amigos.
# O gateway enriquece a compra/desejo com o preço e o título vindos do
# catálogo, mantendo o players-service autônomo (ele só guarda o instantâneo).
# ---------------------------------------------------------------------------
def _find_game(game_id: str) -> dict | None:
    for game in _extract_list(catalog.get("/games")):
        if game.get("id") == game_id:
            return game
    return None


@router.get("/api/players")
def list_players() -> JSONResponse:
    try:
        return _forward(players.get("/players"))
    except Exception:
        return _unavailable(_PLAYERS_DOWN)


@router.post("/api/players")
def create_player(payload: dict = Body(...)) -> JSONResponse:
    try:
        return _forward(players.post("/players", json=payload))
    except Exception:
        return _unavailable("Não foi possível criar o perfil agora. Tente novamente em instantes.")


@router.get("/api/players/{player_id}")
def get_player(player_id: str) -> JSONResponse:
    try:
        return _forward(players.get(f"/players/{player_id}"))
    except Exception:
        return _unavailable(_PLAYERS_DOWN)


@router.post("/api/players/{player_id}/deposit")
def deposit(player_id: str, payload: dict = Body(...)) -> JSONResponse:
    try:
        return _forward(players.post(f"/players/{player_id}/deposit", json=payload))
    except Exception:
        return _unavailable("Não foi possível adicionar saldo agora. Tente novamente em instantes.")


@router.get("/api/store")
def store(playerId: str | None = None) -> JSONResponse:
    """Loja = catálogo + marcação de 'já tenho' / 'na lista de desejos'.

    Degradação parcial: sem o catálogo a loja não existe (503). Sem o
    players-service, a loja aparece sem as marcações do jogador.
    """
    try:
        games = _extract_list(catalog.get("/games"))
    except Exception:
        return _unavailable(_CATALOG_DOWN)

    owned: set[str] = set()
    wished: set[str] = set()
    players_available = True
    if playerId:
        try:
            for entry in _extract_list(players.get(f"/players/{playerId}/library")):
                owned.add(entry.get("gameId"))
            for item in _extract_list(players.get(f"/players/{playerId}/wishlist")):
                wished.add(item.get("gameId"))
        except Exception:
            players_available = False

    catalog_games = [
        {**game, "owned": game.get("id") in owned, "wished": game.get("id") in wished}
        for game in games
    ]
    return JSONResponse(
        status_code=200,
        content={"data": {"games": catalog_games, "playersAvailable": players_available}},
    )


@router.post("/api/players/{player_id}/purchases")
def purchase(player_id: str, payload: dict = Body(...)) -> JSONResponse:
    game_id = (payload or {}).get("gameId")
    if not game_id:
        return _unavailable("Selecione um jogo para comprar.")
    try:
        game = _find_game(game_id)
    except Exception:
        return _unavailable(_CATALOG_DOWN)
    if game is None:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "NAO_ENCONTRADO", "message": "Jogo não encontrado no catálogo."}},
        )
    body = {
        "gameId": game_id,
        "title": game.get("title"),
        "basePriceCents": game.get("priceCents", 0),
    }
    try:
        return _forward(players.post(f"/players/{player_id}/purchases", json=body))
    except Exception:
        return _unavailable("Não foi possível concluir a compra agora. Tente novamente em instantes.")


@router.get("/api/players/{player_id}/library")
def library(player_id: str) -> JSONResponse:
    try:
        return _forward(players.get(f"/players/{player_id}/library"))
    except Exception:
        return _unavailable(_PLAYERS_DOWN)


@router.get("/api/players/{player_id}/wishlist")
def list_wishlist(player_id: str) -> JSONResponse:
    try:
        return _forward(players.get(f"/players/{player_id}/wishlist"))
    except Exception:
        return _unavailable(_PLAYERS_DOWN)


@router.post("/api/players/{player_id}/wishlist")
def add_wishlist(player_id: str, payload: dict = Body(...)) -> JSONResponse:
    game_id = (payload or {}).get("gameId")
    title = (payload or {}).get("title")
    if not title and game_id:
        # Enriquecimento opcional: tenta achar o título no catálogo.
        try:
            game = _find_game(game_id)
            title = game.get("title") if game else None
        except Exception:
            title = None
    try:
        return _forward(
            players.post(f"/players/{player_id}/wishlist", json={"gameId": game_id, "title": title})
        )
    except Exception:
        return _unavailable("Não foi possível atualizar a lista de desejos agora.")


@router.delete("/api/players/{player_id}/wishlist/{game_id}")
def remove_wishlist(player_id: str, game_id: str) -> JSONResponse:
    try:
        return _forward(players.delete(f"/players/{player_id}/wishlist/{game_id}"))
    except Exception:
        return _unavailable("Não foi possível atualizar a lista de desejos agora.")


@router.get("/api/players/{player_id}/friends")
def list_friends(player_id: str) -> JSONResponse:
    try:
        return _forward(players.get(f"/players/{player_id}/friends"))
    except Exception:
        return _unavailable(_PLAYERS_DOWN)


@router.post("/api/players/{player_id}/friends")
def add_friend(player_id: str, payload: dict = Body(...)) -> JSONResponse:
    try:
        return _forward(players.post(f"/players/{player_id}/friends", json=payload))
    except Exception:
        return _unavailable("Não foi possível adicionar o amigo agora. Tente novamente em instantes.")


@router.delete("/api/players/{player_id}/friends/{friend_id}")
def remove_friend(player_id: str, friend_id: str) -> JSONResponse:
    try:
        return _forward(players.delete(f"/players/{player_id}/friends/{friend_id}"))
    except Exception:
        return _unavailable("Não foi possível remover o amigo agora. Tente novamente em instantes.")


@router.get("/api/health")
def health() -> dict:
    return {
        "service": "gateway",
        "status": "ok",
        "downstream": {
            "catalog": catalog.state,
            "reviews": reviews.state,
            "players": players.state,
        },
    }
