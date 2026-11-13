"""Three-table SQL mystery. Only public case tables enter the query sandbox."""
from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
import sys
import threading
from datetime import datetime, timedelta
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CASE_VERSION = 5
TABLES = ("laudo_vitima", "testemunhas", "locais")
LOCK = threading.RLock()


def prepare_case(case: dict) -> dict:
    """Idempotent migration; publish the marker only after dbt and solution checks."""
    folder = Path(case["folder"]) / "sql"
    marker = folder / "ready.json"
    with LOCK:
        if marker.exists():
            cached = json.loads(marker.read_text(encoding="utf-8"))
            if cached.get("version") == CASE_VERSION or case.get("status") in {"solved", "failed"}:
                return cached
        folder.mkdir(exist_ok=True)
        rng = random.Random(case["id"])
        people = pd.read_csv(Path(case["folder"]) / "raw" / "suspects.csv")
        # Expand active cases without changing their culprit or existing people.
        roster = pd.read_csv(ROOT / "data" / "raw" / "suspects.csv")
        additions = roster[~roster.suspect_id.isin(people.suspect_id)]
        people = pd.concat([people, additions], ignore_index=True)
        ids = people.suspect_id.tolist()
        others = [i for i in ids if i != case["killer_id"]]
        rng.shuffle(others)
        # Each innocent fails at least one independent criterion; several lie.
        roles = {case["killer_id"]: (True, True, True)}
        patterns = [(True, True, False), (True, False, True), (False, True, True),
                    (True, False, False), (False, True, False), (False, False, True),
                    (False, False, False)]
        roles.update({person: patterns[index % len(patterns)] for index, person in enumerate(others)})
        moment = datetime.fromisoformat(case["crime_time"]) + timedelta(minutes=rng.randint(-100, 100))
        start, end = moment - timedelta(minutes=10), moment + timedelta(minutes=10)
        shoe = rng.choice([37, 38, 39, 40, 41, 42, 43])
        fiber = rng.choice(["lã azul", "algodão verde", "linho bege", "poliéster preto"])
        locations = [
            ("L001", "Sala do Cofre", "sala restrita", False, "baixa", "Credencial individual", 1),
            ("L002", "Salão Principal", "salão de eventos", True, "alta", "Entrada livre", 35),
            ("L003", "Biblioteca", "sala de leitura", True, "baixa", "Entrada livre", 4),
            ("L004", "Estufa", "jardim coberto", True, "média", "Entrada livre", 12),
        ]
        crime_location = rng.choice(["L001", "L003", "L004"])
        sites = pd.DataFrame(locations, columns=["local_id", "nome", "tipo", "publico", "movimentacao", "acesso", "pessoas_presentes"])
        sites["inicio_registro"] = start - timedelta(hours=1)
        sites["fim_registro"] = end + timedelta(hours=1)
        # Every claimed alibi is at the busy event hall, separate from the crime.
        witnesses = []
        for row in people.sample(frac=1, random_state=rng.randint(0, 99999)).itertuples():
            present, trace, lie = roles[row.suspect_id]
            registered = crime_location if present else "L002"
            witnesses.append({
                "pessoa_id": row.suspect_id, "nome": row.suspect_name, "profissao": row.occupation,
                "inicio_trabalho": moment.replace(hour=16, minute=0),
                "fim_trabalho": moment.replace(hour=23, minute=59),
                "horario_depoimento": end + timedelta(hours=2),
                "horario_relato": moment, "local_declarado_id": "L002" if lie else registered,
                "relato": "Eu estava no salão durante o brinde." if lie else "Permaneci no local que informei à polícia.",
                "alibi": "Participava do brinde no salão." if lie else "Meu registro de acesso confirma onde eu estava.",
                "local_registrado_id": registered,
                "entrada_registrada": start - timedelta(minutes=rng.randint(2, 20)),
                "saida_registrada": end + timedelta(minutes=rng.randint(2, 20)),
                "fonte_registro": "Registro de acesso periciado e confirmado por imagem",
                "numero_calcado": shoe if trace else shoe + rng.choice([-2, 2]),
                "tecido_roupa": fiber if trace else rng.choice([f for f in ["lã azul", "algodão verde", "linho bege", "poliéster preto"] if f != fiber]),
            })
        for idx, site in sites.iterrows():
            recorded = sum(w["local_registrado_id"] == site.local_id for w in witnesses)
            victim = int(site.local_id == crime_location)
            sites.loc[idx, "pessoas_presentes"] = max(int(site.pessoas_presentes), recorded + victim)
        autopsy = pd.DataFrame([{
            "vitima_id": "V001", "nome": "Augusto Valmont", "local_id": crime_location,
            "inicio_morte": start, "fim_morte": end,
            "causa_morte": "Traumatismo craniano", "instrumento": "Objeto metálico contundente",
            "dinamica": "Golpe por trás; fibras retidas na mão da vítima durante a luta.",
            "numero_calcado_vestigio": shoe, "fibra_vestigio": fiber,
            "observacao_pericial": "Pegada recente no sangue e fibras da roupa do agressor. Sem sinais de alteração posterior da cena.",
        }])
        seeds = folder / "seeds"
        seeds.mkdir(exist_ok=True)
        for name, frame in zip(TABLES, [autopsy, pd.DataFrame(witnesses), sites]):
            frame.to_csv(seeds / f"raw_{name}.csv", index=False)
        # Relative seed paths are essential: dbt writes compiled seed artifacts using
        # original_file_path; an absolute seed path can overwrite its source CSV.
        template = ROOT / "sql_game_dbt"
        shutil.copy2(template / "dbt_project.yml", folder / "dbt_project.yml")
        for directory in ("models", "tests"):
            shutil.copytree(template / directory, folder / directory, dirs_exist_ok=True)
        profile = {"sql_game": {"target": "dev", "outputs": {"dev": {
            "type": "duckdb", "path": (folder / "case.duckdb").as_posix(), "threads": 1}}}}
        (folder / "profiles.yml").write_text(json.dumps(profile), encoding="utf-8")
        command = [sys.executable, "-m", "dbt.cli.main", "build", "--project-dir", str(folder),
                   "--profiles-dir", str(folder), "--target-path", str(folder / "target"),
                   "--log-path", str(folder / "logs")]
        try:
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180, env={**os.environ, "DBT_SEND_ANONYMOUS_USAGE_STATS": "false", "DO_NOT_TRACK": "1"})
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("A preparação do caso excedeu o limite. Sua tentativa foi preservada.") from exc
        if result.returncode:
            raise RuntimeError("Não foi possível validar as tabelas SQL. " + result.stdout[-2000:])
        solution = query_case(case, SOLUTION_SQL)
        if solution.pessoa_id.tolist() != [case["killer_id"]]:
            raise RuntimeError("O caso não tem uma solução única; a publicação foi interrompida.")
        culprit = next(w for w in witnesses if w["pessoa_id"] == case["killer_id"])
        location_name = sites.loc[sites.local_id == crime_location, "nome"].iloc[0]
        metadata = {"version": CASE_VERSION, "people_count": len(people), "location": location_name, "crime_time": moment.isoformat(), "proof": [
            f"O laudo situa a morte em {location_name}, entre {start:%H:%M} e {end:%H:%M}.",
            f"O acesso de {case['killer_name']} cobre essa janela: {culprit['entrada_registrada']:%H:%M}–{culprit['saida_registrada']:%H:%M}.",
            f"O depoimento declara o Salão Principal, mas o registro periciado o situa em {location_name}.",
            f"Calçado {shoe} e roupa de {fiber} correspondem aos dois vestígios do laudo. Só essa pessoa reúne os vestígios, a presença e o álibi incompatível.",
        ], "solution_sql": SOLUTION_SQL}
        people.to_csv(Path(case["folder"]) / "raw" / "suspects.csv", index=False)
        marker.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        return metadata


SOLUTION_SQL = """SELECT t.pessoa_id, t.nome
FROM testemunhas t
JOIN laudo_vitima v ON t.local_registrado_id = v.local_id
JOIN locais l ON l.local_id = v.local_id
WHERE t.entrada_registrada <= v.inicio_morte
  AND t.saida_registrada >= v.fim_morte
  AND t.local_declarado_id <> t.local_registrado_id
  AND t.horario_relato BETWEEN v.inicio_morte AND v.fim_morte
  AND t.numero_calcado = v.numero_calcado_vestigio
  AND t.tecido_roupa = v.fibra_vestigio"""


def query_case(case: dict, sql: str) -> pd.DataFrame:
    if not sql.strip() or len(sql) > 20000:
        raise ValueError("Escreva uma consulta de até 20.000 caracteres.")
    database = Path(case["folder"]) / "sql" / "case.duckdb"
    # Never attach the source DB: raw data, internal models and secrets stay outside.
    with duckdb.connect(str(database), read_only=True) as source:
        tables = {name: source.execute(f'SELECT * FROM "{name}"').fetchdf() for name in TABLES}
    with duckdb.connect(":memory:", config={"enable_external_access": "false", "threads": "1", "memory_limit": "128MB", "max_temp_directory_size": "0B"}) as connection:
        for name, frame in tables.items():
            connection.register("input_frame", frame)
            connection.execute(f'CREATE TABLE "{name}" AS SELECT * FROM input_frame')
            connection.unregister("input_frame")
        statements = connection.extract_statements(sql)
        if len(statements) != 1 or statements[0].type != duckdb.StatementType.SELECT:
            raise ValueError("Use uma única consulta SELECT (WITH também é permitido).")
        timer = threading.Timer(3, connection.interrupt)
        timer.start()
        try:
            return connection.execute(f"SELECT * FROM ({statements[0].query.rstrip().rstrip(';')}) AS resultado LIMIT 501").fetchdf()
        finally:
            timer.cancel()
            timer.join()
