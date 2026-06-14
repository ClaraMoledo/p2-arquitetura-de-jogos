# Testes — Ludoteca

Estratégia: **TDD** com `pytest` e **BDD** com `behave` (cenários em português).
Todos os testes usam **repositórios em memória**, então rodam sem banco e sem rede.

## TDD — pytest

| Serviço | Arquivo | Cobre |
|---|---|---|
| catalog-service | `tests/unit/test_game_entity.py` | Regras da entidade `Game`. |
| catalog-service | `tests/unit/test_create_game.py` | Caso de uso de criação. |
| reviews-service | `tests/unit/test_review_entity.py` | Regras da entidade `Review` (nota 1–5). |
| reviews-service | `tests/unit/test_averages.py` | Cálculo de médias por jogo. |
| players-service | `tests/unit/test_player_entity.py` | Carteira: bônus, depósito, cobrança, saldo insuficiente. |
| players-service | `tests/unit/test_pricing.py` | Desconto por fidelidade (Strategy + Factory). |
| players-service | `tests/unit/test_purchase.py` | Compra, duplicidade, sem saldo e amizade simétrica. |
| gateway | `tests/unit/test_circuit_breaker.py` | Abertura, falha rápida e recuperação. |
| gateway | `tests/unit/test_ranking.py` | Ordenação por nota e por lançamento. |

```bash
cd services/catalog-service
pip install -r requirements-dev.txt
pytest -q
```

## BDD — behave

Cenários em `tests/bdd/features/*.feature`, escritos em **português (Gherkin)**, com
passos em `tests/bdd/features/steps/`.

Exemplo (`reviews-service`):

```gherkin
# language: pt
Funcionalidade: Avaliar jogos
  Cenário: Registrar uma avaliação válida
    Dado que não há avaliações para o jogo "jogo-123"
    Quando eu avalio o jogo "jogo-123" com nota 5 assinando como "Marina"
    Então o jogo "jogo-123" deve ter 1 avaliação
    E a média do jogo "jogo-123" deve ser 5.0
```

Exemplo (`players-service`):

```gherkin
# language: pt
Funcionalidade: Comprar jogos na loja
  Cenário: Recusar compra sem saldo suficiente
    Dado um jogador chamado "Pobre" com 1000 centavos na carteira
    Quando ele tenta comprar o jogo "Jogo Caro" por 50000 centavos
    Então a compra deve ser recusada
    E a biblioteca dele deve conter 0 jogos
```

```bash
behave tests/bdd/features
```

## O que está coberto

- Regras de domínio (nota válida, título, ano, preço, saldo da carteira) — unitário.
- Comportamento dos casos de uso (criar, avaliar, calcular média, comprar) — BDD.
- Resiliência (Circuit Breaker) e ordenação/preço (Strategy) — unitário.
