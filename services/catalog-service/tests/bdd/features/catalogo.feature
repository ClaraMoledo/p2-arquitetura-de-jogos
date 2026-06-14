# language: pt
Funcionalidade: Gerenciar o catálogo de jogos
  Para divulgar os jogos disponíveis na loja
  Como administrador do catálogo
  Quero cadastrar e listar jogos

  Cenário: Cadastrar um jogo válido
    Dado que o catálogo está vazio
    Quando eu cadastro o jogo "Stellar Drift" do gênero "Simulação" por 179 reais lançado em 2024
    Então o catálogo deve conter 1 jogo
    E o jogo "Stellar Drift" deve estar disponível

  Cenário: Recusar jogo com ano de lançamento inválido
    Dado que o catálogo está vazio
    Quando eu tento cadastrar o jogo "Tempo Quebrado" lançado em 1900
    Então o cadastro deve ser recusado
