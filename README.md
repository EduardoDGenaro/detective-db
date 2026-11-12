# DetectiveDB — Find the Killer Using SQL

A local investigation game built with Streamlit, DuckDB, and dbt Core. The investigation takes place in an interactive SQL console: you explore three tables, cross-reference testimonies and access logs, and record hypotheses before making your single allowed accusation.

## Running the App

```powershell
.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py --server.headless true --server.port 8501
```

Open `http://localhost:8501`. If you do not have an environment set up yet, install `requirements.txt` inside a Python virtual environment. Opening the app for the first time creates a new match and runs dbt; wait for the preparation step to finish. Bookmark the URL with `?partida=...` to return to the same case.

## The Three Tables

| Table | Contents |
|---|---|
| `laudo_vitima` | Autopsy report, location and time window of death, cause, dynamics, and trace evidence |
| `testemunhas` | Investigated individuals, work shifts, testimonies, alibis, forensic entry/exit logs, and clothing descriptions |
| `locais` | Location type, access rules, activity level, people present, and observed time window |

The location identifier joins the tables. The schema dictionary in the UI lists columns and data types. Start with `SELECT * FROM laudo_vitima;`. Basic SQL examples are provided; the solution is only revealed in the case history after an accusation is made.

The puzzle follows an explicit deductive rule: combine presence during the time window of death, a statement incompatible with that timeframe, and both pieces of trace evidence. Lying alone or matching only one piece of evidence is not enough. Case generation verifies that the full query uniquely identifies the chosen culprit. Contradictions are intentional and are not data integrity errors for dbt to clean up.

## Gameplay Flow and Persistence

- **Investigate with SQL:** Run `SELECT` and `WITH` queries, filters, and `JOIN`s; syntax or query errors do not consume your accusation.
- **Notebook:** Persistent investigation notes with a button to save executed queries.
- **Make an Accusation:** One attempt per case; a wrong guess archives the case and generates a new one with a different killer.
- **History:** Displays the culprit, explanation, solution SQL query, and archived notebook.

Match data is stored under `data/games/<partida>/`. Previous matches preserve their history and notes. Older active cases automatically receive the SQL game dataset when opened. There is no authentication: anyone with the local URL can access the match.

## Transformation and Data Quality with dbt

`sql_game_dbt/` contains the dbt pipeline for the three game tables. Each case generates isolated CSVs, loads seeds, and transforms data using `SELECT` models, type casts, and string trimming. `unique`, `not_null`, relationship, and temporal consistency tests validate the data before publishing the case. Profiles, database files, and artifacts live inside the case's `sql/` directory. The answer is not exposed as a public table.

The SQL console copies only the three final models into an in-memory DuckDB instance. External access is disabled, and write commands or multiple statements are rejected. Query results are capped at 500 rows, with a memory limit and a 3-second execution timeout.

The original course demonstration remains in `notebooks/detective_demo.ipynb`, `detective_dbt/`, and `scripts/`: ingestion, modular transformations, duplicate ID injection, failing test demonstration, and remediation. It uses the original dataset and its own pipeline, while the SQL game uses the pipeline described above. Match preparation currently also maintains legacy marts for compatibility with existing data and tests; those marts are not exposed in the player console.

## Testing

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The test suite covers the end-to-end dbt lifecycle, solution uniqueness, culprit rotation, single-attempt enforcement, notebook persistence, SQL query execution, console safety limits, and Streamlit navigation. Presentation and console tests reuse an existing local match; open the app once before running them.

Current limitation: randomization varies identities, locations, timestamps, and trace evidence, but cases share the same underlying deduction structure. The SQL editor is a plain monospaced text area without autocomplete.
