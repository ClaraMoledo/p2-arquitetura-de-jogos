# SOLID e Padrões — Ludoteca

## SOLID

**S — Responsabilidade Única**
Cada peça tem um motivo para mudar: casos de uso orquestram uma intenção
(`CreateGame`, `AddReview`, `PurchaseGame`); rotas só adaptam HTTP; entidades só
guardam regra (o saldo da carteira mora na entidade `Player`, não no caso de uso).

**O — Aberto/Fechado**
Para mudar a ordenação do ranking, basta adicionar uma nova `RankingStrategy` e
registrá-la na factory — nada do código existente muda
(`gateway/app/ranking/strategies.py`, `factory.py`). O mesmo vale para um novo
desconto: adiciona-se uma `PricingPolicy`
(`services/players-service/app/pricing/`) sem tocar no `PurchaseGame`.

**L — Substituição de Liskov**
`SqlGameRepository` e `InMemoryGameRepository` implementam a mesma porta
`GameRepository`; os casos de uso funcionam com qualquer um, sem saber a diferença.
O mesmo para os repositórios de jogadores, biblioteca, desejos e amizades.

**I — Segregação de Interface**
Portas pequenas e específicas: `GameRepository` (save/list_all),
`ReviewRepository` (save/list_by_game/list_all), `RankingStrategy` (order),
`LibraryRepository`, `WishlistRepository`, `FriendshipRepository`, `PricingPolicy`.

**D — Inversão de Dependência**
Casos de uso recebem o repositório por abstração; quem decide a implementação é a
factory (`app/infra/factory.py`), e a injeção é feita pelos `Depends`
(`app/api/dependencies.py`).

## Padrões de projeto

### Repository
Isola o domínio da persistência.
- Porta: `app/domain/repositories.py` (Protocol).
- Implementações: `app/infra/sql_repository.py` (SQLAlchemy) e `app/infra/memory.py`.

### Strategy
Algoritmos intercambiáveis sob uma mesma interface.
- Ranking: `gateway/app/ranking/strategies.py` — `RankByRatingStrategy`, `RankByRecentStrategy`.
- Preço de compra: `services/players-service/app/pricing/strategies.py` —
  `StandardPricing`, `WelcomePricing` (primeira compra), `VeteranPricing` (fidelidade).

### Factory
Cria o objeto concreto certo.
- `app/infra/factory.py`: repositório SQL ou em memória conforme o ambiente.
- `gateway/app/ranking/factory.py`: estratégia de ranking a partir do parâmetro.
- `services/players-service/app/pricing/factory.py`: política de preço a partir do
  tamanho da biblioteca do jogador.

### Aggregator / BFF
O gateway combina vários serviços numa só resposta para o frontend.
- `gateway/app/api/routes.py`: `/api/ranking` (catálogo + médias) e `/api/store`
  (catálogo + biblioteca/desejos do jogador), ambos com degradação parcial.

### Circuit Breaker
Evita falhas em cascata e respostas penduradas.
- `gateway/app/infra/circuit_breaker.py`: estados CLOSED → OPEN → HALF_OPEN.
- Testado em `gateway/tests/unit/test_circuit_breaker.py`.

### Adapter
Adapta a API de baixo nível do httpx a uma interface conveniente (`get`/`post`),
embrulhando timeout e Circuit Breaker.
- `gateway/app/infra/service_client.py`.

### Injeção de Dependência (FastAPI Depends)
A montagem do grafo de dependências fica nos provedores de `app/api/dependencies.py`,
consumidos via `Depends` nas rotas.
