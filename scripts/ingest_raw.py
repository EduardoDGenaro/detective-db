"""
Script de ingestao da camada bruta (raw) para o projeto DetectiveDB.
Carrega os cinco arquivos CSV ficticios para o schema `raw` no DuckDB.
Pode ser reexecutado de forma idempotente (CREATE OR REPLACE TABLE).
"""

from pathlib import Path
import sys
import duckdb


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
DB_PATH = PROJECT_ROOT / "data" / "detectivedb.duckdb"

RAW_TABLES = {
    "suspects": "suspects.csv",
    "evidence": "evidence.csv",
    "testimonies": "testimonies.csv",
    "cameras": "cameras.csv",
    "locations": "locations.csv",
}


def ingest_raw_tables(db_path: Path = DB_PATH, raw_dir: Path = RAW_DATA_DIR) -> dict[str, int]:
    """Recria o schema raw e carrega os 5 arquivos CSV no DuckDB."""
    missing_files = [
        csv_name for csv_name in RAW_TABLES.values() if not (raw_dir / csv_name).exists()
    ]
    if missing_files:
        raise FileNotFoundError(
            f"Arquivos CSV ausentes em {raw_dir}: {', '.join(missing_files)}"
        )

    db_path.parent.mkdir(parents=True, exist_ok=True)
    row_counts: dict[str, int] = {}

    with duckdb.connect(str(db_path)) as con:
        con.execute("CREATE SCHEMA IF NOT EXISTS raw;")

        for table_name, csv_filename in RAW_TABLES.items():
            csv_path = (raw_dir / csv_filename).as_posix()
            con.execute(
                f"""
                CREATE OR REPLACE TABLE raw.{table_name} AS
                SELECT *
                FROM read_csv_auto('{csv_path}', header=true, nullstr='');
                """
            )
            count = con.execute(f"SELECT COUNT(*) FROM raw.{table_name};").fetchone()[0]
            row_counts[table_name] = int(count)

    return row_counts


def main() -> int:
    print("[INFO] Iniciando ingestao da camada raw no DuckDB...")
    print(f"[INFO] Banco alvo: {DB_PATH}")
    try:
        counts = ingest_raw_tables()
    except Exception as exc:
        print(f"[ERRO] Falha durante a ingestao: {exc}", file=sys.stderr)
        return 1

    for table_name, count in counts.items():
        print(f"[OK] Tabela raw.{table_name} carregada com {count} registros.")

    print("[OK] Ingestao concluida com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

