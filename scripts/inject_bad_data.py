"""
Script de experimento de qualidade de dados para o DetectiveDB.
Insere propositalmente um registro duplicado de evidencia (evidence_id = 'E001')
na tabela `raw.evidence` para demonstrar a deteccao de falha pelo `dbt test`.
"""

from pathlib import Path
import sys
import duckdb


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "detectivedb.duckdb"


def inject_duplicate_evidence(db_path: Path = DB_PATH, target_id: str = "E001") -> tuple[int, int]:
    """Insere uma copia de `target_id` em `raw.evidence` e retorna (total_linhas, ocorrencias_id)."""
    if not db_path.exists():
        raise FileNotFoundError(
            f"Banco DuckDB nao encontrado em {db_path}. Execute scripts/ingest_raw.py primeiro."
        )

    with duckdb.connect(str(db_path)) as con:
        exists = con.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'raw' AND table_name = 'evidence';
            """
        ).fetchone()[0]
        if not exists:
            raise RuntimeError(
                "Tabela raw.evidence nao existe. Execute scripts/ingest_raw.py primeiro."
            )

        con.execute(
            """
            INSERT INTO raw.evidence
            SELECT *
            FROM raw.evidence
            WHERE evidence_id = ?
            LIMIT 1;
            """,
            [target_id],
        )

        total_rows = con.execute("SELECT COUNT(*) FROM raw.evidence;").fetchone()[0]
        dup_count = con.execute(
            "SELECT COUNT(*) FROM raw.evidence WHERE evidence_id = ?;",
            [target_id],
        ).fetchone()[0]

    return int(total_rows), int(dup_count)


def main() -> int:
    target_id = "E001"
    print(f"[INFO] Injetando duplicidade proposital em raw.evidence (evidence_id = '{target_id}')...")
    try:
        total_rows, dup_count = inject_duplicate_evidence(target_id=target_id)
    except Exception as exc:
        print(f"[ERRO] Nao foi possivel injetar a anomalia: {exc}", file=sys.stderr)
        return 1

    print(
        f"[ALERTA] Anomalia injetada: raw.evidence possui agora {total_rows} linhas "
        f"({dup_count} ocorrencias para evidence_id = '{target_id}')."
    )
    print("[INFO] Execute `dbt test --profiles-dir .` em `detective_dbt/` para verificar a falha.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

