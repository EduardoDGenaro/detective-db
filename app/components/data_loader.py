"""
Modulo de acesso a dados e artefatos dbt para a interface Streamlit.
Utiliza conexoes efemeras em modo somente-leitura para nao bloquear
o arquivo DuckDB durante execucoes do pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "detectivedb.duckdb"
DBT_TARGET_DIR = PROJECT_ROOT / "detective_dbt" / "target"
RUN_RESULTS_PATH = DBT_TARGET_DIR / "run_results.json"
MANIFEST_PATH = DBT_TARGET_DIR / "manifest.json"

REQUIRED_MART_TABLES = [
    "dim_suspects",
    "dim_locations",
    "fct_evidence",
    "fct_testimonies",
    "fct_camera_events",
    "mart_case_summary",
]


def check_database_status(db_path: Path = DB_PATH) -> dict[str, Any]:
    """Verifica a existencia do arquivo DuckDB e das tabelas raw e marts."""
    status: dict[str, Any] = {
        "db_exists": db_path.exists(),
        "db_path": str(db_path),
        "raw_tables": [],
        "mart_tables": [],
        "ready": False,
        "error": None,
    }
    if not db_path.exists():
        return status

    try:
        with duckdb.connect(str(db_path), read_only=True) as con:
            tables_df = con.execute(
                """
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_schema IN ('raw', 'main')
                ORDER BY table_schema, table_name;
                """
            ).df()

        raw_tables = tables_df[tables_df["table_schema"] == "raw"]["table_name"].tolist()
        main_tables = tables_df[tables_df["table_schema"] == "main"]["table_name"].tolist()
        mart_present = [t for t in REQUIRED_MART_TABLES if t in main_tables]

        status["raw_tables"] = raw_tables
        status["mart_tables"] = mart_present
        status["ready"] = len(mart_present) == len(REQUIRED_MART_TABLES)
    except Exception as exc:
        status["error"] = str(exc)

    return status


def query_df(sql: str, params: list[Any] | None = None, db_path: Path = DB_PATH) -> pd.DataFrame:
    """Executa uma consulta somente-leitura no DuckDB e fecha a conexao imediatamente."""
    with duckdb.connect(str(db_path), read_only=True) as con:
        if params:
            return con.execute(sql, params).df()
        return con.execute(sql).df()


def load_investigative_datasets(db_path: Path = DB_PATH) -> dict[str, pd.DataFrame]:
    """Carrega os modelos analiticos produzidos pelo dbt."""
    def query(sql: str) -> pd.DataFrame:
        return query_df(sql, db_path=db_path)
    return {
        "summary": query(
            "SELECT * FROM main.mart_case_summary ORDER BY investigation_priority_rank ASC, suspect_id ASC"
        ),
        "suspects": query("SELECT * FROM main.dim_suspects ORDER BY suspect_id ASC"),
        "locations": query("SELECT * FROM main.dim_locations ORDER BY location_id ASC"),
        "evidence": query(
            "SELECT * FROM main.fct_evidence ORDER BY collected_at ASC, evidence_id ASC"
        ),
        "testimonies": query(
            "SELECT * FROM main.fct_testimonies ORDER BY claimed_event_time ASC, testimony_id ASC"
        ),
        "cameras": query(
            "SELECT * FROM main.fct_camera_events ORDER BY seen_at ASC, camera_event_id ASC"
        ),
    }


def load_raw_evidence_duplicates(db_path: Path = DB_PATH) -> pd.DataFrame:
    """Consulta duplicidades reais de `evidence_id` na camada `raw.evidence`."""
    if not db_path.exists():
        return pd.DataFrame()
    try:
        return query_df(
            """
            SELECT
                evidence_id,
                suspect_id,
                location_id,
                evidence_type,
                collected_at,
                status,
                COUNT(*) AS occurrence_count
            FROM raw.evidence
            GROUP BY
                evidence_id,
                suspect_id,
                location_id,
                evidence_type,
                collected_at,
                status
            HAVING COUNT(*) > 1
            ORDER BY occurrence_count DESC, evidence_id ASC;
            """, db_path=db_path
        )
    except Exception:
        return pd.DataFrame()


def load_dbt_quality_report(target_dir: Path = DBT_TARGET_DIR) -> dict[str, Any]:
    """
    Le os artefatos reais `run_results.json` e `manifest.json` gerados pelo dbt.
    Nao inventa status caso os arquivos ainda nao existam.
    """
    report: dict[str, Any] = {
        "available": False,
        "is_test_run": False,
        "generated_at": None,
        "invocation_command": None,
        "elapsed_time": None,
        "dbt_version": None,
        "counts": {"pass": 0, "fail": 0, "warn": 0, "error": 0, "skipped": 0, "total": 0},
        "results_df": pd.DataFrame(),
    }

    run_results_path = target_dir / "run_results.json"
    manifest_path = target_dir / "manifest.json"
    if not run_results_path.exists():
        return report

    try:
        run_results = json.loads(run_results_path.read_text(encoding="utf-8"))
        manifest_nodes: dict[str, Any] = {}
        if manifest_path.exists():
            manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest_nodes = manifest_data.get("nodes", {})

        metadata = run_results.get("metadata", {})
        args = run_results.get("args", {})
        which_cmd = args.get("which", "")
        invocation_cmd = args.get("invocation_command", "")

        rows = []
        counts = {"pass": 0, "fail": 0, "warn": 0, "error": 0, "skipped": 0, "total": 0}

        for item in run_results.get("results", []):
            unique_id = item.get("unique_id", "")
            status = str(item.get("status", "")).lower()
            node_info = manifest_nodes.get(unique_id, {})
            resource_type = node_info.get(
                "resource_type",
                "test" if unique_id.startswith("test.") else "model",
            )
            node_name = node_info.get("name", unique_id.split(".")[-1])

            if resource_type == "test" and status in counts:
                counts[status] += 1

            rows.append(
                {
                    "unique_id": unique_id,
                    "resource_type": resource_type.upper(),
                    "name": node_name,
                    "status": status.upper(),
                    "failures": item.get("failures"),
                    "execution_time_s": round(float(item.get("execution_time", 0.0)), 4),
                    "message": item.get("message") or "",
                }
            )

        results_df = pd.DataFrame(rows)
        is_test_run = (which_cmd == "test") or (
            not results_df.empty and (results_df["resource_type"] == "TEST").any()
        )
        counts["total"] = counts["pass"] + counts["fail"] + counts["warn"] + counts["error"]

        report.update(
            {
                "available": True,
                "is_test_run": is_test_run,
                "which_command": which_cmd,
                "generated_at": metadata.get("generated_at"),
                "dbt_version": metadata.get("dbt_version"),
                "invocation_command": invocation_cmd,
                "elapsed_time": round(float(run_results.get("elapsed_time", 0.0)), 3),
                "counts": counts,
                "results_df": results_df,
            }
        )
    except Exception as exc:
        report["error"] = str(exc)

    return report
