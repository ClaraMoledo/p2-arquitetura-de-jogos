# 🎮 Ludoteca

Plataforma de **loja, catálogo e comunidade de jogos**. Os jogadores navegam pela
loja, **compram jogos** com a **carteira**, montam a **biblioteca** e a **lista de
desejos**, adicionam **amigos**, avaliam títulos com nota de 1 a 5 e conferem um
**ranking** dinâmico.

Construída como um conjunto de **microsserviços** em **Python/FastAPI**, seguindo
**Arquitetura Limpa**, **SOLID**, **Design Patterns**, **TDD** e **BDD**, tudo
orquestrado com **Docker Compose** e publicado em servidor.

> **Aluna:** Ana Clara Moledo Neves · Universidade de Vassouras (Maricá) · Arquitetura de Software
> **App no ar:** [Link do Ludoteca](https://p2-arquitetura-de-software-ludoteca.n5ywgm.easypanel.host/)

---

## Como rodar (resumo rápido)

```bash
cp .env.example .env
docker compose up --build
# abre em http://localhost:8090
```

Pronto: catálogo populado, avaliações de exemplo e ranking funcionando.

## O problema

Quem curte games vive a mesma dúvida: _"esse jogo vale a pena?"_ — e ainda quer um
lugar para **comprar, colecionar e acompanhar os amigos**. As informações ficam
espalhadas e as notas misturam opiniões de fontes diferentes. A **Ludoteca** junta,
em um só lugar:

- uma **loja** com catálogo de jogos (título, gênero, plataforma, preço, ano);
- **compra** de jogos com **carteira/saldo** e desconto automático por fidelidade;
- **biblioteca** (jogos comprados) e **lista de desejos** por jogador;
- **amigos** entre jogadores (relação simétrica);
- **avaliações** da comunidade (nota + comentário);
- um **ranking** que combina catálogo e notas, ordenável por melhores avaliações
  ou por lançamentos mais recentes.

Tudo isso resistindo a quedas: se um banco sai do ar, o usuário vê um **aviso
gentil**, nunca um erro técnico (mais em [Resiliência](#resiliência)).

## Os microsserviços

| Serviço | Papel | Porta | Banco |
|---|---|---|---|
| `web` | SPA + proxy `/api` (nginx) | 80 | — |
| `gateway` | BFF: roteia, agrega ranking e loja, Circuit Breaker | 8000 | — |
| `catalog-service` | Catálogo de jogos | 8001 | `catalog-db` |
| `reviews-service` | Avaliações e médias | 8002 | `reviews-db` |
| `players-service` | Jogadores, carteira, compras, biblioteca, desejos e amigos | 8003 | `players-db` |

```
  navegador → web (nginx) → gateway ┬→ catalog-service → catalog-db
                                    ├→ reviews-service → reviews-db
                                    └→ players-service → players-db
```

Cada serviço tem **seu próprio banco** (padrão _database per service_) e não enxerga
o banco do outro. O gateway é o único ponto que fala com os três — e é onde mora a
lógica de **ranking**, da **loja** (catálogo + posse do jogador) e de **resiliência**.

## Arquitetura Limpa por dentro

Cada serviço usa as mesmas camadas, com dependências apontando para o centro:

```
app/
├── domain/      → entidades + regras (Game, Review, Player, LibraryEntry…) e portas
├── use_cases/   → casos de uso (CreateGame, AddReview, PurchaseGame, AddFriend…)
├── pricing/     → políticas de preço por fidelidade (Strategy) — players-service
├── infra/       → SQLAlchemy, settings, fábricas, repositório em memória
└── api/         → rotas FastAPI, schemas, tratadores de erro
```

O `domain` não importa FastAPI nem SQLAlchemy. A escolha da implementação concreta
(banco x memória) acontece nas **factories** de `infra`, e a injeção é feita pelos
`Depends` do FastAPI. Veja [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md).

## SOLID na prática

- **S** — cada caso de uso resolve uma intenção; rotas só adaptam HTTP. A regra de
  saldo da carteira mora na entidade `Player`, não no caso de uso.
- **O** — novas formas de ordenar o ranking entram como novas `RankingStrategy`, e
  novos descontos como novas `PricingPolicy`, sem tocar no resto.
- **L** — repositórios SQLAlchemy e em memória são intercambiáveis pela mesma porta.
- **I** — portas enxutas (`GameRepository`, `ReviewRepository`, `LibraryRepository`…).
- **D** — casos de uso dependem de abstrações, recebidas por injeção.

Detalhes com arquivos em [`docs/PADROES-SOLID.md`](docs/PADROES-SOLID.md).

## Padrões de projeto (6)

| Padrão | Onde |
|---|---|
| Repository | `app/domain/repositories.py` + `app/infra/{sql_repository,memory}.py` |
| Strategy | `gateway/app/ranking/strategies.py` (ranking) e `players-service/app/pricing/strategies.py` (desconto por fidelidade) |
| Factory | `app/infra/factory.py`, `gateway/app/ranking/factory.py` e `players-service/app/pricing/factory.py` |
| Circuit Breaker | `gateway/app/infra/circuit_breaker.py` |
| Adapter | `gateway/app/infra/service_client.py` (httpx + breaker) |
| Aggregator (BFF) | `gateway/app/api/routes.py` — `/api/store` e `/api/ranking` juntam vários serviços |

## Clean Code

Nomes claros, funções curtas, valores monetários em **centavos** (sem `float`),
configuração por variáveis de ambiente, camadas isoladas e erros de domínio
explícitos. Sem mágica escondida.

## Testes

**TDD (pytest)** e **BDD (behave, em português)** — todos rodam **sem banco**,
usando repositórios em memória.

```bash
cd services/catalog-service
pip install -r requirements-dev.txt
pytest -q                  # unitários
behave tests/bdd/features  # comportamento
```

O mesmo vale para `services/reviews-service` e `services/players-service` (este
cobre carteira, compra com saldo insuficiente, compra duplicada, fidelidade e
amizades). O `gateway` tem `pytest`. Mais em [`docs/TESTES.md`](docs/TESTES.md).

## Resiliência

> Requisito de ouro: **derrubar um banco não pode derrubar o sistema**, e o usuário
> não pode ver nada técnico.

- Os serviços **sobem mesmo sem banco** (migração roda em thread, repetindo).
- Erro de conexão → **HTTP 503 com mensagem amigável**.
- O gateway tem **Circuit Breaker**: serviço fora = falha rápida e amigável.
- O **ranking degrada parcialmente**: se as avaliações caírem, ele aparece sem as
  notas, em vez de quebrar.
- A **loja degrada parcialmente**: se o `players-db` cair, ela ainda lista os jogos,
  apenas sem as marcações de "já tenho"/"desejado".

Demonstração:

```bash
docker compose stop reviews-db   # derruba o banco de avaliações
# Catálogo segue funcionando; o ranking aparece sem notas, com aviso gentil.
docker compose start reviews-db  # volta sozinho

docker compose stop players-db   # derruba o banco de jogadores
# A loja segue listando jogos; perfil/carteira respondem com aviso gentil.
docker compose start players-db  # volta sozinho
```

## Deploy

Publicado via **Docker Compose** (EasyPanel). A entrada pública é o serviço `web`,
exposto por domínio; o gateway e os microsserviços ficam na rede interna, e cada banco
roda em seu próprio contêiner. O link da aplicação no ar está no topo deste README.

## Onde cada critério está

| Critério | Seção / caminho |
|---|---|
| Problema e solução | "O problema" |
| Clean Code | "Clean Code" |
| SOLID | "SOLID na prática" + `docs/PADROES-SOLID.md` |
| Design Patterns | "Padrões de projeto" |
| Arquitetura Limpa | "Arquitetura Limpa por dentro" + `docs/ARQUITETURA.md` |
| Microsserviços | "Os microsserviços" |
| TDD | `tests/unit` + "Testes" |
| BDD | `tests/bdd` + "Testes" |
| Docker | `docker-compose.yml` + "Como rodar (resumo rápido)" |
| Deploy | "Deploy" + link no topo |
| Justificativas | `docs/ARQUITETURA.md` |

---

Construído com FastAPI e SQLAlchemy. Licença MIT.
