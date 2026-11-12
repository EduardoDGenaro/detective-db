# Revisão atual — investigação por SQL (12/11/2026)

Resultado final: suíte completa com 6 testes aprovada em 155,164 s. Após acrescentar a regressão dos CSVs, os 4 testes do console foram aprovados em 6,291 s. Captura final em artifacts/investigacao-sql-final.jpg. Aplicação disponível em localhost:8501.

A navegação anterior foi substituída por console SQL, caderno, acusação e histórico. Abaixo ficam os registros históricos das revisões do dashboard, que não descrevem mais o produto atual.

Revisão visual: desktop 1366×768 e celular 390×844. Editor monoespaçado, dicionário contextual, resultados com rolagem interna. Corrigido o cabeçalho que ficava sob a barra móvel; menu móvel inicia recolhido. Sem overflow horizontal da página nas medições. Editor reduzido para aproximar os resultados da consulta.

Verificações funcionais: SELECT/WITH/JOIN reais, resultado vazio, SQL inválido, tentativa de escrita, tentativa de leitura de arquivos, tabelas privadas indisponíveis, limite de linhas, interrupção de consulta cara, persistência e arquivamento do caderno. Ciclo de erro/acerto e troca de culpado com dbt real; solução única verificada antes de publicar cada caso.

Correções durante a validação: telemetria dbt desabilitada para evitar espera externa; projetos dbt isolados com seed-paths relativos, pois caminhos absolutos podiam fazer artefatos compilados sobrescreverem os CSVs. Acrescentada regressão verificando os CSVs após o build.

Autocrítica: a experiência agora pede raciocínio SQL, sem painéis que destacam respostas. Ainda é um enigma introdutório com lógica repetida entre casos e editor sem autocompletar. Exemplos de JOIN e descrição das colunas ajudam quem está começando. As regras de dedução estão explícitas e são regras de um jogo, não uma simulação jurídica de prova criminal.

---

# Verificação da interface e regras

## Dossiê integrado, comparação de fontes e caderno

Implementados os itens 1, 2, 3 e 5 aprovados pelo usuário:

- Nomes clicáveis na visão geral e na lista abrem um dossiê com abas de resumo, álibis/depoimentos, evidências e câmeras. É possível trocar de pessoa dentro da ficha e voltar à lista.
- Comparações mostram os locais e horários declarados ao lado dos registros reais da mesma pessoa na janela de cinco minutos. A seleção reproduz a regra de fronteiras de minuto do `date_diff` usado no dbt. Registros compatíveis também são identificados; ausência de imagem não confirma o álibi.
- Notas e pistas marcadas ficam no JSON da partida, por caso. O servidor valida a origem das pistas no DuckDB e recusa alterações após o encerramento. Cada novo caso tem um caderno vazio. O arquivo do caso anterior conserva o texto e as descrições marcadas.
- Indicadores e gráfico de qualidade saíram da visão geral; o relatório continua no menu, em Ferramentas técnicas.

Validação: integração real com geração de três casos e dbt; preservação do caderno após erro e acerto; marcação idempotente; recusa de referências inválidas, textos acima do limite e alterações em caso antigo. Teste específico da janela de comparação e exclusão de câmeras de outra pessoa. Streamlit AppTest das nove páginas e teste de interação para abrir ficha, trocar pessoa, marcar pista, escrever, navegar, reabrir em nova sessão e consultar arquivo somente para leitura.

No navegador foi usado um estado de partida separado para não alterar as hipóteses do jogador. Marcar T001 e salvar uma nota sobreviveram ao recarregamento e ao reinício do servidor. Comparação conferida em 1366px (duas colunas) e 390px (uma coluna), sem transbordamento dos blocos nem largura extra da página.

## Remoção da pontuação e revisão de clareza

A interface de investigação deixou de exibir a pontuação interna: removidos a coluna, o filtro, o cartão do dossiê, a memória de cálculo, a posição de prioridade e a pontuação dos seletores. Listas agora seguem ordem alfabética, com IDs e contagens reais de evidências. Avisos antigos sobre pontuação também não são apresentados no histórico. O modelo analítico didático continua disponível no pipeline.

**Autocrítica:** a tela anterior destacava uma heurística como se fosse uma resposta pronta e obrigava o jogador a interpretar termos de implementação. O contexto de uso e os botões genéricos não explicavam bem o próximo passo. A tabela de suspeitos tinha colunas demais para uma primeira exploração. Os painéis com alturas diferentes deixavam um vazio que parecia falta de conteúdo.

**Correções:** instrução curta de investigação na visão geral; ações “Abrir dossiês”, “Explorar”, “Conferir álibis” e “Ver testes”; tabela inicial com seis colunas; dossiê com três cartões; filtros de triagem e situação das evidências em português; linha do tempo identificada como o caso atual. Contradições inclui dois exemplos de depoimento/câmera a conferir. Os pares de painéis ficam alinhados na mesma altura, com indicadores compactos.

**Validação no navegador:** em 1568px, os painéis inferiores mediram 248px cada; em 1366px, 268px; em 1024px, 328px. Em 390px eles se empilham e seguem a altura natural de cada conteúdo. Nas quatro larguras não houve transbordamento dos indicadores nem rolagem horizontal da página. Os painéis superiores também ficaram alinhados (375px no exemplo a 1568px). Nenhuma pontuação foi encontrada no texto da visão geral. A navegação “Abrir dossiês” abriu a ficha sem pontuação ou ranking.

Foi incluído um teste de apresentação para as oito telas e para a ausência do filtro, coluna e valores da pontuação no seletor: `python -m unittest discover -s tests -p test_ui_presentation.py -v`.

**Avaliação de intuitividade:** o caminho para investigar e acusar está mais explícito. As tabelas de evidências e câmeras continuam densas por conterem dados de análise e têm rolagem própria. Esta é uma inspeção de interface e fluxo, não uma pesquisa com jogadores; não comprova que todo usuário entenderá o caso sem ajuda.

## Reavaliação de formatação após o transbordamento no dossiê

A revisão visual inicial foi insuficiente: testar a renderização das páginas e a visão geral não cobria os cartões com nomes e estados longos. O exemplo enviado pelo usuário revelou um problema de prioridade alta de leitura e encaixe.

| Problema encontrado | Causa | Correção |
| --- | --- | --- |
| Nome e status ultrapassavam o cartão | Altura fixa de 128px e fonte de 41,6px para qualquer valor | Altura orientada pelo conteúdo, texto a 20,8px e números até 40px |
| Palavras quebradas no meio e rótulos sobre a borda | Mesmo componente de número usado para frases em caixa alta | Escala própria para texto, rótulos curtos e quebra natural |
| Informações de apoio encostavam no bloco seguinte | Cartão HTML dentro do fluxo Markdown | Renderização com `st.html`, sem compensações de margem do Markdown |
| Quatro colunas estreitas em janelas menores | Adaptação baseada só na janela | Colunas adaptadas à largura efetiva do conteúdo: quatro, duas ou uma |
| Ícone de confirmação para um conflito | Ícone genérico de fallback | Alerta vermelho para conflito e ícone informativo para outros valores |

Validação geométrica no navegador: dossiê em 1568, 1366, 1024, 768 e 390px. Foram medidos os retângulos de títulos, valores e textos de apoio e o `scrollWidth/scrollHeight` de cada cartão. Nenhum transbordamento foi identificado nos casos medidos; a largura do documento permaneceu igual à da janela. Os quatro cartões ficaram com 168px de altura em desktop e 128px no celular nos exemplos verificados; conteúdo maior pode aumentar a altura.

Também foram medidos os indicadores de visão geral, evidências, qualidade e configurações em desktop, além dos indicadores de evidências no celular. Foi conferido o nome mais longo “Eduardo Montenegro” em quatro colunas a 1366px, sem corte ou sobreposição. As oito páginas passaram novamente pelo Streamlit AppTest sem exceções. As tabelas analíticas mantêm sua rolagem interna para colunas extensas.

Esta conferência valida os estados e larguras medidos, sem representar uma garantia para todo conteúdo possível. A prévia e as medições estão em `artifacts/`.

Validação realizada em 12/11/2026.

- Integração Python: `python -m unittest discover -s tests -v` aprovado. O teste constrói três casos com dbt real, verifica culpado diferente no caso seguinte, acusação inválida, repetição da tentativa, acerto, retomada, preservação do histórico e falha de pipeline sem perda de tentativa.
- Pipeline: 96 testes dbt aprovados por caso gerado, incluindo relacionamentos, unicidade e consistência temporal.
- Streamlit AppTest: as oito páginas renderizaram sem exceções; enviar acusação vazia exibiu validação e preservou a tentativa.
- Navegador: acusação errada arquivou o caso 001, revelou assassino e provas no histórico e abriu o caso 002. Atualização e reinício do servidor preservaram o estado pela URL da partida.
- Layout: conferência visual em 1366×768 e 390×844; no celular, a largura do documento permaneceu em 390px, sem rolagem horizontal da página. Título mobile com 26px e controles nativos de formulário com rótulos.
- Revisão manual: tema escuro nativo, foco visível, campos de 16px, redução de movimento e tabelas com pontuação em pontos. Miniaturas são ilustrações; contagens, provas e resultados vêm do DuckDB e dos artefatos do caso ativo.

Correções de coerência: o caso jogável inclui narrativa de homicídio e laudo conclusivo; a heurística não determina a culpa. A regra temporal dbt acompanha a data sorteada. O experimento didático de duplicidades continua separado das partidas.

Limites: sem autenticação; cada URL representa uma partida compartilhável. A exclusão mútua das transições considera o servidor de processo único usado neste projeto. A randomização combina as pistas do cenário original com novas provas conclusivas; não gera narrativas inteiramente inéditas.
