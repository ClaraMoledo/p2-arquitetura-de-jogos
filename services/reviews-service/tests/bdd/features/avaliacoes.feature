# language: pt
Funcionalidade: Avaliar jogos
  Para ajudar outros jogadores a escolher
  Como jogador
  Quero avaliar um jogo com uma nota de 1 a 5

  Cenário: Registrar uma avaliação válida
    Dado que não há avaliações para o jogo "jogo-123"
    Quando eu avalio o jogo "jogo-123" com nota 5 assinando como "Marina"
    Então o jogo "jogo-123" deve ter 1 avaliação
    E a média do jogo "jogo-123" deve ser 5.0

  Cenário: Recusar nota fora do intervalo
    Dado que não há avaliações para o jogo "jogo-123"
    Quando eu tento avaliar o jogo "jogo-123" com nota 9 assinando como "Bruno"
    Então a avaliação deve ser recusada
