# DetectiveDB — Caso 001: O Relogio Parado

## Modo de investigação jogável

### Investigar, comparar e anotar

- Clique no nome de uma pessoa na visão geral ou na lista de suspeitos para abrir seu **dossiê integrado**. As abas reúnem resumo, álibis e depoimentos, evidências completas e câmeras dessa pessoa.
- Em **Contradições**, cada depoimento aparece ao lado dos registros reais de câmera da mesma pessoa e janela de tempo, com horários e locais. “Abrir dossiê” leva diretamente à ficha correspondente.
- Use **Marcar no caderno** nas evidências, depoimentos e câmeras. O **Caderno de investigação** guarda as pistas escolhidas e suas hipóteses. O texto é salvo ao sair do campo; “Salvar agora” permite confirmar o salvamento explicitamente.
- Ao acusar, o caderno é arquivado com o caso, tanto no erro quanto no acerto. Casos novos começam com caderno vazio. No histórico, as anotações e pistas encerradas ficam disponíveis apenas para leitura. Partidas anteriores sem caderno continuam compatíveis.
- A **Qualidade dos Dados** continua acessível em **Ferramentas técnicas**, no menu. O dashboard mostra somente informações de investigação e o acesso ao caderno.

Anotações têm limite de 10.000 caracteres por caso. Pistas marcadas incluem uma cópia de referência, descrição, pessoa, horário e local obtida do DuckDB. Salvar uma nota ou marcar uma pista não consome a chance de acusação.

A interface agora apresenta um homicídio fictício na Mansão Valmont ligado ao desaparecimento do relógio. A base didática abaixo continua disponível; cada partida gera suas próprias fontes e executa `dbt build` em um DuckDB isolado.

Execute `.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py` e abra a URL local indicada. O primeiro caso é preparado automaticamente, sem exigir ingestão manual.

- **Fazer acusação:** escolha um suspeito e confirme a regra de uma única chance.
- **Se errar:** o caso é arquivado e outro é gerado automaticamente, obrigatoriamente com assassino diferente. Vínculos entre suspeitos, provas, depoimentos e câmeras, idades, triagem, datas e identificadores das provas conclusivas são randomizados de forma consistente.
- **Se acertar:** o caso é encerrado; o botão “Investigar novo caso” inicia outra investigação.
- **Histórico dos casos:** mostra o assassino, sua acusação, provas conclusivas e os dados arquivados de cada caso encerrado.

Partidas e histórico ficam em `data/games/`, fora do versionamento. Preserve a URL com `?partida=...` para retomar a mesma partida após atualizar ou reiniciar o servidor. Sem esse identificador, abre-se uma nova partida. Não há autenticação: quem possui o link pode acessar a partida. A solução não é enviada à interface durante a investigação.

Uma nova investigação só é publicada quando o pipeline passa. Falha na preparação preserva a tentativa e o histórico. O bloqueio de transições atende ao servidor Streamlit de processo único usado neste projeto. Os scripts `inject_bad_data.py` e `reset_demo.py` continuam operando apenas no banco didático original.

Validação de integração: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`. O teste executa o dbt real, verifica erro/acerto, troca obrigatória de culpado, duplicação de tentativa, persistência, arquivo histórico e recuperação de falha no pipeline.

Laboratorio pratico de Engenharia de Dados com tematica investigativa, construido com **Python**, **DuckDB**, **dbt Core** (`dbt-duckdb`) e **Streamlit**.

> [!IMPORTANT]
> **Proposito Didatico e Metodologico:** O foco central deste projeto e demonstrar ingestao reprodutivel, modelagem analitica modular em SQL (`source()` e `ref()`), testes automatizados de qualidade de dados e observabilidade em uma interface conectada ao banco real. O indicador `suspicion_score` e uma **heuristica exploratoria ficticia** e nunca deve ser interpretado como probabilidade estatistica de culpa ou veredito.

---

## 1. Contexto do Caso Investigativo

Durante uma recepcao noturna na **Mansao Valmont** em `14/10/2026`, o cronometro astronomico de bolso **Relogio Breguet 1794** desapareceu da Sala do Cofre e Relojoaria (`L001`). Os ponteiros do mecanismo secundario pararam exatamente as `22:15:00`.

Cinco fontes de dados brutas em formato CSV chegam para analise:

| Fonte CSV (`data/raw/`) | Registros | Descricao |
|---|---:|---|
| `suspects.csv` | 8 | Cadastro preliminar de pessoas presentes na mansao e nivel de triagem inicial (`risk_level`). |
| `locations.csv` | 8 | Ambientes internos (`INDOOR`) e externos (`OUTDOOR`) monitorados na propriedade. |
| `evidence.csv` | 20 | Vestigios periciais coletados (incluindo itens sem suspeito identificado e pistas descartadas). |
| `testimonies.csv` | 14 | Depoimentos colhidos com horario e local alegados de forma estruturada (`claimed_location_id`, `claimed_event_time`). |
| `cameras.csv` | 28 | Capturas de cameras de seguranca com timestamp (`seen_at`) e identificacao visual. |

---

## 2. Arquitetura e Linhagem de Dados

```text
5 Arquivos CSV (data/raw/*.csv)
      |
      v
Python (scripts/ingest_raw.py)
      |
      v
DuckDB — Schema: raw
  |-- raw.suspects
  |-- raw.locations
  |-- raw.evidence
  |-- raw.testimonies
  +-- raw.cameras
      |
      v
dbt Core — Camada Staging (Views em main.stg_*)
  |-- stg_suspects      (source: raw.suspects)
  |-- stg_locations     (source: raw.locations)
  |-- stg_evidence      (source: raw.evidence)
  |-- stg_testimonies   (source: raw.testimonies)
  +-- stg_cameras       (source: raw.cameras)
      |
      v
dbt Core — Camada Marts (Tabelas em main.*)
  |-- dim_suspects
  |-- dim_locations
  |-- fct_evidence
  |-- fct_camera_events
  |-- fct_testimonies
  +-- mart_case_summary
      |
      v
Interface Streamlit (app/streamlit_app.py) + Auditoria (run_results.json)
```

### Decisoes de Engenharia para Prevencao de Erros Comuns

1. **Prevencao de Fan-Out em Joins (`mart_case_summary.sql`):** Evidencias, depoimentos e eventos de camera sao pre-agregados individualmente por `suspect_id` em CTEs separadas antes do `LEFT JOIN` com `dim_suspects`, impedindo a multiplicacao artificial de contagens.
2. **Transparencia na Camada Staging (`stg_evidence.sql`):** Registros com `suspect_id` ausente (vestigios ainda nao atribuidos a uma pessoa) sao mantidos com `suspect_id = NULL` e demarcados com `is_suspect_identified = FALSE`. Nao ha uso de `SELECT DISTINCT` silencioso sobre chaves primarias para nao mascarar falhas de duplicidade nos testes.
3. **Deteccao Estruturada de Contradicoes de Alibi (`fct_testimonies.sql`):** Compara `claimed_event_time` e `claimed_location_id` de cada depoimento com `seen_at` e `location_id` dos registros de camera do mesmo suspeito, sinalizando conflito quando o suspeito e visto em local distinto dentro de uma janela de ate **5 minutos**.

---

## 3. Regra do Score Heuristico (`mart_case_summary`)

A pontuacao de priorizacao investigativa segue a formula deterministica centralizada no SQL:

```text
suspicion_score =
    2 * evidence_count
  + 3 * inconsistent_testimony_count
  + 2 * suspicious_location_events
  + 4 * alibi_camera_conflict_count
```

Onde `suspicious_location_events` contabiliza capturas de camera em zonas de acesso restrito/critico (`L001` Sala do Cofre, `L004` Corredor Subterraneo e `L007` Garagem e Portao Leste).

---

## 4. Estrutura do Repositorio

```text
detectivedb/
├── data/
│   ├── raw/
│   │   ├── suspects.csv
│   │   ├── evidence.csv
│   │   ├── testimonies.csv
│   │   ├── cameras.csv
│   │   └── locations.csv
│   └── detectivedb.duckdb              # gerado; ignorado pelo Git
├── detective_dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── models/
│   │   ├── sources.yml
│   │   ├── staging/
│   │   │   ├── stg_suspects.sql
│   │   │   ├── stg_evidence.sql
│   │   │   ├── stg_testimonies.sql
│   │   │   ├── stg_cameras.sql
│   │   │   └── stg_locations.sql
│   │   └── marts/
│   │       ├── dim_suspects.sql
│   │       ├── dim_locations.sql
│   │       ├── fct_evidence.sql
│   │       ├── fct_testimonies.sql
│   │       ├── fct_camera_events.sql
│   │       └── mart_case_summary.sql
│   ├── tests/
│   │   ├── assert_evidence_time_consistency.sql
│   │   └── assert_nonnegative_suspicion_score.sql
│   └── target/                         # gerado; ignorado pelo Git
├── scripts/
│   ├── ingest_raw.py
│   ├── inject_bad_data.py
│   └── reset_demo.py
├── app/
│   ├── streamlit_app.py
│   ├── components/
│   │   ├── cards.py
│   │   └── data_loader.py
│   └── styles/
│       └── theme.py
├── notebooks/
│   └── detective_demo.ipynb
├── assets/
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 5. Como Instalar e Executar Localmente

### 5.1. Criar ambiente virtual e instalar dependencias

No Windows (PowerShell):

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

No Linux / macOS:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 5.2. Executar ingestao e pipeline dbt (Estado Valido)

A partir da raiz do projeto:

```bash
python scripts/ingest_raw.py
cd detective_dbt
dbt debug --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
dbt docs generate --profiles-dir .
cd ..
```

Resultado esperado no estado integro:
- `dbt run`: **11 modelos construidos com sucesso** (5 views `staging` + 6 tabelas `marts`).
- `dbt test`: **96 testes aprovados (`PASS=96 WARN=0 ERROR=0`)**, cobrindo `unique`, `not_null`, `relationships`, `accepted_values` e os 2 testes SQL personalizados (`assert_nonnegative_suspicion_score` e `assert_evidence_time_consistency`).

### 5.3. Reproduzir o Experimento de Qualidade (Falha e Recuperacao)

**Passo A — Injetar duplicidade proposital na fonte (`raw.evidence`):**

```bash
python scripts/inject_bad_data.py
cd detective_dbt
dbt test --profiles-dir .
```

Resultado real obtido:
- O script duplica o registro `evidence_id = 'E001'` em `raw.evidence` (passando de 20 para 21 linhas).
- O comando `dbt test` detecta a violacao e falha nos testes `source_unique_raw_evidence_evidence_id`, `unique_stg_evidence_evidence_id` e `unique_fct_evidence_evidence_id` (`Got 1 result, configured to fail if != 0`).

**Passo B — Restaurar a fonte e revalidar o pipeline:**

```bash
cd ..
python scripts/reset_demo.py
cd detective_dbt
dbt run --profiles-dir .
dbt test --profiles-dir .
cd ..
```

Resultado real obtido:
- `raw.evidence` volta a ter 20 registros unicos e todos os **96 testes voltam a passar (`PASS=96 ERROR=0`)**.

---

## 6. Iniciar a Interface Streamlit

A partir da raiz do repositorio:

```bash
streamlit run app/streamlit_app.py
```

A interface usa conexoes DuckDB efemeras em modo somente-leitura (`read_only=True`) e os PNGs de `assets/` como identidade visual e miniaturas ilustrativas. A home apresenta quatro indicadores calculados a partir dos marts e dos testes dbt, os quatro principais suspeitos, as tres evidencias mais recentes, conflitos de alibi sem contagem duplicada e a qualidade da ultima execucao real.

1. **Visao geral:** quatro KPIs, cinco principais suspeitos, feed de evidencias, resumo de contradicoes e qualidade dbt.
2. **Suspeitos:** filtros por risco, contradicao, score e busca, com dossie individual detalhado.
3. **Evidencias:** catalogo filtravel por status, tipo, local e suspeito; as imagens sao apenas ilustracoes por categoria.
4. **Contradicoes:** possiveis conflitos de alibi/camera e cronologia unificada, segundo a regra centralizada no dbt.
5. **Qualidade dos Dados:** resultados de testes em `detective_dbt/target/run_results.json`, sem contar modelos ou testes ignorados como aprovados.
6. **Configuracoes:** caminhos do DuckDB e dos artefatos, estado da conexao e atualizacao da leitura.

O campo de pesquisa filtra suspeitos, evidencias e locais. O `suspicion_score` permanece uma heuristica de priorizacao definida no SQL; a barra do ranking e comparativa e nao representa probabilidade de culpa. O dashboard nao executa ingestao nem dbt automaticamente.

---

## 7. Execucao no Google Colab

O arquivo [`notebooks/detective_demo.ipynb`](notebooks/detective_demo.ipynb) contem o roteiro completo e autocontido para execucao no Google Colab ou em Jupyter local, documentando:
- Instalacao de `dbt-core`, `dbt-duckdb`, `duckdb` e `pandas`.
- Ingestao da camada `raw`.
- Execucao inicial (`PASS=96`).
- Injecao de duplicidade com captura da falha (`ERROR=2`).
- Restauracao com `reset_demo.py` e nova bateria de testes (`PASS=96`).
- Consulta SQL analitica exibindo `mart_case_summary` e os conflitos de alibi.

