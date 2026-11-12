# DetectiveDB — investigação por SQL

O jogador descobre o assassino escrevendo SQL sobre três tabelas públicas: laudo_vitima, testemunhas e locais. Não há ranking, score, lista de contradições pronta ou evidência que nomeie automaticamente o culpado.

Fluxo: consultar o laudo, explorar o esquema, filtrar pessoas, cruzar horários e locais, registrar hipóteses no caderno e fazer uma acusação. A regra didática exige combinar presença na janela da morte, declaração incompatível e os dois vestígios. Há inocentes que mentem e inocentes que combinam com vestígios; um indício isolado não encerra o caso.

Quatro páginas: Investigar com SQL, Caderno de investigação, Fazer acusação e Histórico dos casos. A ajuda ensina sintaxe e semântica das colunas, sem mostrar a consulta-resposta durante o caso ativo.

Uma acusação por caso. Errar arquiva solução e caderno e gera dados novos com outro assassino. Acertar encerra o caso e permite iniciar outro. Falha de preparação preserva a tentativa. Casos antigos mantêm notas e histórico; o caso ativo ganha as três tabelas na primeira abertura.

SQL somente leitura em banco em memória contendo apenas as tabelas públicas, sem acesso externo, limitado a 500 linhas exibidas e 3 segundos de execução. É um jogo local, com identidade pela URL da partida; não é uma aplicação multiusuário autenticada.
