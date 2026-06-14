# language: pt
Funcionalidade: Comprar jogos na loja
  Para montar minha biblioteca
  Como jogador da Ludoteca
  Quero comprar jogos usando o saldo da carteira

  Cenário: Comprar um jogo com saldo suficiente
    Dado um jogador chamado "Nova" com 20000 centavos na carteira
    Quando ele compra o jogo "Aurora Frontier" por 10000 centavos
    Então a compra deve ser concluída
    E a biblioteca dele deve conter 1 jogo

  Cenário: Recusar compra sem saldo suficiente
    Dado um jogador chamado "Pobre" com 1000 centavos na carteira
    Quando ele tenta comprar o jogo "Jogo Caro" por 50000 centavos
    Então a compra deve ser recusada
    E a biblioteca dele deve conter 0 jogos

  Cenário: Recusar comprar duas vezes o mesmo jogo
    Dado um jogador chamado "Nova" com 20000 centavos na carteira
    Quando ele compra o jogo "Aurora Frontier" por 5000 centavos
    E ele tenta comprar o jogo "Aurora Frontier" por 5000 centavos
    Então a compra deve ser recusada
    E a biblioteca dele deve conter 1 jogo
