# Arquitetura — Ludoteca

## Visão geral

A Ludoteca é um sistema de **microsserviços** em Python/FastAPI. Internamente, cada
serviço segue a **Arquitetura Limpa**, separando regra de negócio de detalhes de
tecnologia.

```
navegador
   │
   ▼
 web (nginx + SPA)            entrada pública, proxy /api
   │
   ▼
 gateway (BFF, :8000)         roteia, agrega ranking e loja, Circuit Breaker
   ├──────────────► catalog-service (:8001) ──► catalog-db
   ├──────────────► reviews-service (:8002) ──► reviews-db
   └──────────────► players-service (:8003) ──► players-db
```

## Por que dividir assim?

Três contextos independentes: **catálogo** (dados quase estáticos), **avaliações**
(crescem o tempo todo e têm regras próprias, como nota de 1 a 5) e **jogadores**
(carteira, compras, biblioteca, desejos e amigos — o lado transacional). Separá-los
permite:

- evoluir/escalar cada um isoladamente;
- isolar falhas — se o banco de jogadores cai, a loja continua mostrando o catálogo;
- bancos independentes (_database per service_).

O **gateway (BFF)** existe para servir bem o frontend: ele junta dados dos serviços
(ranking, e a loja = catálogo + posse do jogador) e concentra a resiliência, deixando
os serviços de domínio simples.

## Camadas (Clean Architecture)

| Camada | Pasta | Depende de | Exemplos |
|---|---|---|---|
| Entidades/Domínio | `app/domain` | nada externo | `Game`, `Review`, `Player`, portas |
| Casos de uso | `app/use_cases` | domínio | `CreateGame`, `PurchaseGame`, `AddFriend` |
| Políticas de preço | `app/pricing` | domínio | `WelcomePricing`, `VeteranPricing` (players) |
| Infraestrutura | `app/infra` | domínio | `SqlGameRepository`, `factory` |
| Interface (API) | `app/api` | casos de uso | rotas FastAPI, schemas |

A regra de dependência aponta sempre para dentro. As **portas** ficam no domínio
(`repositories.py` como `Protocol`); as implementações ficam na infraestrutura. A
inversão é resolvida pelas factories + `Depends` do FastAPI.

## Fluxo: registrar uma avaliação

`POST /api/games/{id}/reviews`:

1. `web` faz proxy para o `gateway`.
2. `gateway` chama o `reviews-service` via `ServiceClient` (httpx + timeout + breaker).
3. `reviews-service` → rota → caso de uso `AddReview`.
4. `AddReview` cria a entidade `Review` (valida nota 1–5, autor, jogo).
5. `ReviewRepository` (SQLAlchemy) persiste.

Se o banco estiver fora, o erro vira **503 amigável** antes de chegar ao usuário.

## Ranking (agregação)

O endpoint `/api/ranking` do gateway:

1. busca os jogos no catálogo;
2. busca as médias no `reviews-service`;
3. junta as duas informações (`average`, `reviewCount`) por jogo;
4. aplica uma **estratégia de ordenação** (`RankingStrategy`): por nota ou por
   lançamento.

Se as avaliações estiverem indisponíveis, o ranking ainda sai (sem as notas):
**degradação parcial** em vez de falha total.

## Loja e compra (agregação + transação)

A **loja** (`GET /api/store?playerId=`) é outra agregação do gateway: pega os jogos do
catálogo e marca, para o jogador atual, o que ele **já tem** (biblioteca) e o que está
na **lista de desejos**. Se o `players-service` cair, a loja ainda lista os jogos.

A **compra** (`POST /api/players/{id}/purchases`) mostra o gateway como _enricher_:

1. o frontend manda só o `gameId`;
2. o gateway busca o jogo no catálogo (título + preço) e repassa ao `players-service`;
3. o caso de uso `PurchaseGame` escolhe a **política de preço** conforme a fidelidade
   (Strategy + Factory), **cobra a carteira** (regra na entidade `Player`), grava o
   jogo na **biblioteca** e o remove dos **desejos**.

Assim o `players-service` continua autônomo: ele guarda um _instantâneo_ do título e do
preço pago, sem depender do catálogo para funcionar depois.

## Dados

- **catalog-db** → `games` (id, title, genre, platform, price_cents, release_year, available).
- **reviews-db** → `reviews` (id, game_id, author, rating, comment, created_at).
- **players-db** → `players` (id, name, wallet_cents), `library_entries`,
  `wishlist_items`, `friendships`.

Preços são **inteiros em centavos** (sem ponto flutuante). Avaliações, biblioteca e
desejos guardam `game_id` como referência fraca — nenhum serviço depende do banco do
outro para funcionar.

## Resiliência

| Mecanismo | Onde |
|---|---|
| Boot sem banco + retry de migração | `app/main.py` (`_init_db_with_retry`, em thread) |
| Timeout curto de conexão | `app/infra/database.py` (`connect_timeout`) |
| Erro de conexão → 503 amigável | `app/infra/errors.py` + `app/api/errors.py` |
| Circuit Breaker | `gateway/app/infra/circuit_breaker.py` |
| Degradação parcial do ranking e da loja | `gateway/app/api/routes.py` |

## Justificativas técnicas

- **FastAPI**: rápido, tipado, com injeção de dependência nativa (`Depends`), ideal
  para microsserviços pequenos.
- **SQLAlchemy 2.0**: ORM maduro; `pool_pre_ping` ajuda a sobreviver a quedas de banco.
- **httpx**: cliente HTTP moderno com timeout simples, usado no Adapter do gateway.
- **Circuit Breaker próprio**: padrão explícito e testável, sem dependência extra.
- **nginx**: serve o SPA e concentra `/api` na mesma origem (sem CORS).
