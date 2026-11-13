"""End-to-end Streamlit navigation, SQL execution and notebook persistence."""
from pathlib import Path
import unittest
import json
import sys
import tempfile
from uuid import uuid4
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
from components import case_game
from components.sql_case import prepare_case

class PresentationTests(unittest.TestCase):
    def test_sql_notebook_and_archive(self):
        original = json.loads(next((ROOT / "data/games").glob("*/game.json")).read_text(encoding="utf-8"))["active"]
        with tempfile.TemporaryDirectory() as directory, patch.object(case_game, "GAMES", Path(directory)):
            game_id = str(uuid4())
            (Path(directory) / game_id).mkdir()
            case = {**original, "status": "active", "notebook": {"notes": "", "clues": {}}}
            case["sql_game"] = prepare_case(case)
            case["proof"] = case["sql_game"]["proof"]
            case_game.save_game(game_id, {"active": case, "history": []})
            app = AppTest.from_file(str(ROOT / "app/streamlit_app.py"), default_timeout=60)
            app.query_params["partida"] = game_id
            app.run()
            self.assertFalse(app.exception)
            labels = [b.label for b in app.button]
            self.assertNotIn("Contradições", labels)
            self.assertNotIn("Evidências", labels)
            app.text_area[0].set_value("SELECT nome FROM testemunhas ORDER BY nome;")
            next(b for b in app.button if b.label == "Executar consulta").click().run()
            self.assertFalse(app.exception)
            self.assertTrue(any(len(f.value) == 32 for f in app.dataframe))
            next(b for b in app.button if b.label == "Guardar consulta no caderno").click().run()
            next(b for b in app.button if b.label == "Caderno de investigação").click().run()
            self.assertIn("SELECT nome", app.text_area[0].value)
            app.text_area[0].set_value("Minha hipótese e consulta SQL.").run()
            self.assertEqual(case_game.load_game(game_id)["active"]["notebook"]["notes"], "Minha hipótese e consulta SQL.")
            for page in ["Fazer acusação", "Histórico dos casos", "Investigar com SQL"]:
                next(b for b in app.button if b.label == page).click().run()
                self.assertFalse(app.exception)
            app.text_area[0].set_value("DELETE FROM testemunhas")
            next(b for b in app.button if b.label == "Executar consulta").click().run()
            self.assertTrue(app.error)
            self.assertFalse(app.exception)
            self.assertEqual(case_game.load_game(game_id)["active"]["status"], "active")
            case_game.accuse(game_id, case["id"], case["killer_id"])
            next(b for b in app.button if b.label == "Caderno de investigação").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.text_area), 0)
            next(b for b in app.button if b.label == "Histórico dos casos").click().run()
            self.assertTrue(any("Minha hipótese" in str(t.value) for t in app.text))
            self.assertTrue(any("SELECT t.pessoa_id" in str(t.value) for t in app.code))

if __name__ == "__main__":
    unittest.main()
