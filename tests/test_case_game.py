"""Integração real de uma partida, incluindo os marts e testes dbt."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from components import case_game as game
from components.sql_case import query_case, SOLUTION_SQL
from components.data_loader import load_investigative_datasets, load_dbt_quality_report


class CaseGameIntegration(unittest.TestCase):
    def test_full_game_lifecycle(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(game, "GAMES", Path(directory)):
            game_id, initial = game.start_game()
            first = initial["active"]
            self.assertEqual(query_case(first, SOLUTION_SQL).pessoa_id.tolist(), [first["killer_id"]])
            first_folder = Path(first["folder"])
            before = load_investigative_datasets(first_folder / "case.duckdb")
            quality = load_dbt_quality_report(first_folder / "target")
            self.assertEqual(quality["counts"]["pass"], quality["counts"]["total"])
            self.assertGreater(quality["counts"]["total"], 0)
            forensic = before["evidence"].query("evidence_type == 'LAUDO_FORENSE'")
            self.assertEqual(forensic.suspect_id.tolist(), [first["killer_id"]])
            self.assertEqual(len(before["summary"]), 32)
            clue_id = str(before["evidence"].iloc[0]["evidence_id"])
            game.save_notes(game_id, first["id"], "Conferir o horário do depoimento e a perícia.")
            marked = game.pin_clue(game_id, first["id"], "evidence", clue_id, True)
            self.assertEqual(marked["active"]["notebook"]["notes"], "Conferir o horário do depoimento e a perícia.")
            self.assertEqual(marked["active"]["notebook"]["clues"][f"evidence:{clue_id}"]["detail"],
                             before["evidence"].iloc[0]["evidence_description"])
            # Marcar novamente é idempotente e não apaga o texto salvo por outra ação.
            self.assertEqual(len(game.pin_clue(game_id, first["id"], "evidence", clue_id, True)["active"]["notebook"]["clues"]), 1)
            with self.assertRaises(ValueError):
                game.pin_clue(game_id, first["id"], "evidence", "INVALID", True)
            with self.assertRaises(ValueError):
                game.save_notes(game_id, first["id"], "x" * 10001)
            initial = game.load_game(game_id)
            wrong = next(value for value in before["summary"].suspect_id if value != first["killer_id"])
            with patch.object(game, "generate_case", side_effect=RuntimeError("pipeline indisponível")):
                with self.assertRaises(RuntimeError):
                    game.accuse(game_id, first["id"], wrong)
            self.assertEqual(game.load_game(game_id), initial)
            with self.assertRaises(ValueError):
                game.accuse(game_id, first["id"], "INVALID")
            failed = game.accuse(game_id, first["id"], wrong)
            second = failed["active"]
            self.assertNotEqual(first["killer_id"], second["killer_id"])
            self.assertEqual(second["number"], 2)
            self.assertEqual(query_case(second, SOLUTION_SQL).pessoa_id.tolist(), [second["killer_id"]])
            self.assertNotEqual(first["sql_game"], second["sql_game"])
            self.assertEqual(failed["history"][0]["killer_id"], first["killer_id"])
            self.assertEqual(failed["history"][0]["status"], "failed")
            self.assertEqual(failed["history"][0]["notebook"], initial["active"]["notebook"])
            self.assertEqual(second["notebook"], {"notes": "", "clues": {}})
            with self.assertRaises(ValueError):
                game.save_notes(game_id, first["id"], "Não pode editar o arquivo")
            with self.assertRaises(ValueError):
                game.pin_clue(game_id, first["id"], "evidence", clue_id, False)
            self.assertTrue(before["evidence"].equals(load_investigative_datasets(first_folder / "case.duckdb")["evidence"]))
            with self.assertRaises(ValueError):
                game.accuse(game_id, first["id"], first["killer_id"])
            solved = game.accuse(game_id, second["id"], second["killer_id"])
            self.assertEqual(solved["active"]["status"], "solved")
            self.assertEqual(len(solved["history"]), 2)
            with self.assertRaises(ValueError):
                game.save_notes(game_id, second["id"], "Caso já encerrado")
            self.assertEqual(game.load_game(game_id), solved)
            with self.assertRaises(ValueError):
                game.accuse(game_id, second["id"], wrong)
            restarted = game.next_investigation(game_id, second["id"])
            self.assertEqual(restarted["active"]["number"], 3)
            self.assertNotEqual(restarted["active"]["killer_id"], second["killer_id"])
            self.assertEqual(restarted["history"], solved["history"])


if __name__ == "__main__":
    unittest.main()
