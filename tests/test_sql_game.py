"""Public SQL boundary and logical solvability of real dbt-built cases."""
import json
from pathlib import Path
import sys
import unittest

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
from components.sql_case import prepare_case, query_case, SOLUTION_SQL


class SqlGameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = json.loads(next((ROOT / "data/games").glob("*/game.json")).read_text(encoding="utf-8"))["active"]
        prepare_case(cls.case)

    def test_solution_requires_multiple_clues(self):
        case = self.case
        self.assertEqual(query_case(case, SOLUTION_SQL).pessoa_id.tolist(), [case["killer_id"]])
        self.assertGreater(len(query_case(case, "SELECT * FROM testemunhas WHERE local_declarado_id <> local_registrado_id")), 1)
        self.assertGreater(len(query_case(case, "SELECT t.* FROM testemunhas t JOIN laudo_vitima v ON t.numero_calcado = v.numero_calcado_vestigio AND t.tecido_roupa = v.fibra_vestigio")), 1)
        self.assertEqual(len(query_case(case, "WITH pessoas AS (SELECT * FROM testemunhas) SELECT * FROM pessoas;")), 32)

    def test_sql_is_read_only_and_cannot_reach_private_data(self):
        for sql in ["DELETE FROM testemunhas", "SELECT 1; SELECT 2", "COPY testemunhas TO 'leak.csv'",
                    "SELECT * FROM raw_testemunhas", "SELECT * FROM main.fct_evidence",
                    "SELECT * FROM read_text('README.md')", "SELECT * FROM read_csv_auto('data/raw/suspects.csv')",
                    "ATTACH 'data/detective.duckdb' AS private", "INSTALL httpfs", "SET enable_external_access=true"]:
            with self.subTest(sql=sql), self.assertRaises((ValueError, duckdb.Error)):
                query_case(self.case, sql)
        self.assertEqual(len(query_case(self.case, "SELECT * FROM testemunhas")), 32)
        self.assertEqual(len(query_case(self.case, "SELECT * FROM range(1000)")), 501)
        self.assertTrue(query_case(self.case, "SELECT * FROM testemunhas WHERE 1=0").empty)

    def test_seed_files_remain_valid_csv_after_dbt_build(self):
        seeds = Path(self.case["folder"]) / "sql" / "seeds"
        for name, rows in [("laudo_vitima", 1), ("testemunhas", 32), ("locais", 4)]:
            self.assertEqual(len(pd.read_csv(seeds / f"raw_{name}.csv")), rows)

    def test_expensive_query_is_interrupted(self):
        with self.assertRaises(duckdb.Error):
            query_case(self.case, "SELECT sum(a.i*b.i) FROM range(100000000) a(i), range(100000000) b(i)")


if __name__ == "__main__":
    unittest.main()
