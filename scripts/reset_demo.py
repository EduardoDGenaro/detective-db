"""
Script de restauracao do estado integro do DetectiveDB.
Reexecuta a carga limpa da camada `raw` a partir dos CSVs originais,
removendo anomalias injetadas no experimento de qualidade.
"""

from pathlib import Path
import sys

from ingest_raw import DB_PATH, ingest_raw_tables


def main() -> int:
    print("[INFO] Restaurando camada raw a partir dos arquivos CSV originais...")
    try:
        counts = ingest_raw_tables()
    except Exception as exc:
        print(f"[ERRO] Falha ao restaurar o banco {DB_PATH}: {exc}", file=sys.stderr)
        return 1

    for table_name, count in counts.items():
        print(f"[OK] Tabela raw.{table_name} restaurada ({count} registros integros).")

    print("[OK] Estado inicial restaurado. Execute `dbt run` e `dbt test` para validar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

