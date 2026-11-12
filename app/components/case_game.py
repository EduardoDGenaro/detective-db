"""Casos isolados por partida; cada transição publica estado e histórico juntos."""
from __future__ import annotations

import json
import os
import random
import subprocess
import sys
import threading
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
GAMES = ROOT / "data" / "games"
LOCK = threading.RLock()


def game_directory(game_id: str) -> Path:
    return GAMES / str(UUID(game_id))


def save_game(game_id: str, state: dict) -> None:
    path = game_directory(game_id) / "game.json"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def load_game(game_id: str) -> dict:
    return json.loads((game_directory(game_id) / "game.json").read_text(encoding="utf-8"))


def _editable_case(state: dict, case_id: str) -> dict:
    case = state["active"]
    if case["id"] != case_id or case["status"] != "active":
        raise ValueError("Este caso já foi encerrado. O caderno arquivado permanece preservado.")
    return case


def save_notes(game_id: str, case_id: str, notes: str) -> dict:
    if not isinstance(notes, str) or len(notes) > 10000:
        raise ValueError("As anotações devem ter até 10.000 caracteres.")
    with LOCK:
        state = load_game(game_id)
        case = _editable_case(state, case_id)
        notebook = case.setdefault("notebook", {"notes": "", "clues": {}})
        notebook["notes"] = notes
        notebook["saved_at"] = datetime.now().isoformat()
        save_game(game_id, state)
        return state


def pin_clue(game_id: str, case_id: str, kind: str, reference_id: str, pinned: bool) -> dict:
    """Muda só a pista solicitada; descrição e vínculos vêm do banco do caso."""
    from .data_loader import load_investigative_datasets
    sources = {"evidence": ("evidence", "evidence_id", "evidence_description", "collected_at"),
               "testimony": ("testimonies", "testimony_id", "statement", "claimed_event_time"),
               "camera": ("cameras", "camera_event_id", "camera_label", "seen_at")}
    if kind not in sources or not isinstance(pinned, bool):
        raise ValueError("Tipo de pista inválido.")
    with LOCK:
        state = load_game(game_id)
        case = _editable_case(state, case_id)
        table, id_column, detail_column, time_column = sources[kind]
        data = load_investigative_datasets(Path(case["folder"]) / "case.duckdb")[table]
        matches = data[data[id_column] == reference_id]
        if len(matches) != 1:
            raise ValueError("A pista não pertence ao caso atual.")
        notebook = case.setdefault("notebook", {"notes": "", "clues": {}})
        key = f"{kind}:{reference_id}"
        if pinned:
            row = matches.iloc[0]
            location = "claimed_location_name" if kind == "testimony" else "location_name"
            notebook["clues"][key] = {"kind": kind, "id": reference_id,
                "suspect_id": None if pd.isna(row["suspect_id"]) else str(row["suspect_id"]),
                "suspect_name": str(row["suspect_name"]), "detail": str(row[detail_column]),
                "location": str(row[location]), "time": str(row[time_column])}
        else:
            notebook["clues"].pop(key, None)
        notebook["saved_at"] = datetime.now().isoformat()
        save_game(game_id, state)
        return state


def generate_case(game_id: str, number: int, previous_killer: str | None = None) -> dict:
    """Randomiza fontes e reconstrói os marts com dbt antes de publicar o caso."""
    rng = random.SystemRandom()
    folder = game_directory(game_id) / f"case-{number:03d}-{uuid4().hex[:8]}"
    raw = folder / "raw"
    raw.mkdir(parents=True)
    frames = {name: pd.read_csv(ROOT / "data" / "raw" / f"{name}.csv", keep_default_na=False)
              for name in ("suspects", "locations", "evidence", "testimonies", "cameras")}
    ids = frames["suspects"]["suspect_id"].tolist()
    killer = rng.choice([item for item in ids if item != previous_killer])
    remaining = [item for item in ids if item != killer]
    rng.shuffle(remaining)
    mapping = dict(zip(ids, [killer] + remaining))
    # Todos os vínculos mudam juntos: nenhuma pista mantém a identidade anterior.
    for name, frame in frames.items():
        if name != "suspects" and "suspect_id" in frame:
            frame["suspect_id"] = frame["suspect_id"].map(lambda value: mapping.get(value, value))
    suspects = frames["suspects"]
    original = suspects.set_index("suspect_id")
    for old_id, new_id in mapping.items():
        suspects.loc[suspects.suspect_id == new_id, "alibi"] = original.loc[old_id, "alibi"]
    suspects["age"] = [rng.randint(27, 65) for _ in ids]
    suspects["risk_level"] = [rng.choice(["LOW", "MEDIUM", "HIGH"]) for _ in ids]
    frames["testimonies"]["statement"] = frames["testimonies"]["statement"].str.replace(
        "ouvir o discurso do anfitriao", "ouvir o anuncio do desaparecimento", regex=False)
    # Mantém horários estruturados iguais aos horários citados nos textos livres.
    offset = timedelta(days=rng.randint(1, 300))
    for frame in frames.values():
        for column in ("collected_at", "statement_time", "claimed_event_time", "seen_at"):
            if column in frame:
                frame[column] = (pd.to_datetime(frame[column]) + offset).dt.strftime("%Y-%m-%dT%H:%M:%S")
    crime_time = datetime(2026, 10, 14, 22, 15) + offset
    forensic_id = f"E{rng.randint(100, 999)}"
    dna = "Perfil genético na arma do crime corresponde exclusivamente a este suspeito; sangue da vítima confirmado na mesma peça."
    frames["evidence"].loc[len(frames["evidence"])] = [
        forensic_id, killer, "L001", "LAUDO_FORENSE", dna,
        (crime_time + timedelta(hours=2)).isoformat(), "ANALYZED"]
    video_id = f"C{rng.randint(100, 999)}"
    frames["cameras"].loc[len(frames["cameras"])] = [
        video_id, killer, "L001", crime_time.isoformat(), "CAM-COFRE-PERICIADA"]
    for name, frame in frames.items():
        frame.to_csv(raw / f"{name}.csv", index=False)
    # A base didática original continua disponível para os scripts de demonstração.
    sys.path.insert(0, str(ROOT / "scripts")) if str(ROOT / "scripts") not in sys.path else None
    from ingest_raw import ingest_raw_tables
    database = folder / "case.duckdb"
    ingest_raw_tables(database, raw)
    profile = {"detective_dbt": {"target": "dev", "outputs": {"dev": {
        "type": "duckdb", "path": database.as_posix(), "schema": "main", "threads": 1}}}}
    # JSON é um subconjunto válido de YAML para o profiles.yml do dbt.
    (folder / "profiles.yml").write_text(json.dumps(profile), encoding="utf-8")
    command = [sys.executable, "-m", "dbt.cli.main", "build", "--project-dir", str(ROOT / "detective_dbt"),
               "--profiles-dir", str(folder), "--target-path", str(folder / "target"),
               "--log-path", str(folder / "logs")]
    try:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180, env={**os.environ, "DBT_SEND_ANONYMOUS_USAGE_STATS": "false", "DO_NOT_TRACK": "1"})
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("O pipeline demorou além do limite. Sua tentativa foi preservada; tente novamente.") from exc
    if result.returncode:
        raise RuntimeError("Não foi possível preparar o novo caso. A tentativa foi preservada.\n" + result.stdout[-3500:] + result.stderr[-1000:])
    killer_name = suspects.loc[suspects.suspect_id == killer, "suspect_name"].iloc[0]
    case = {"id": uuid4().hex, "number": number, "folder": str(folder), "killer_id": killer,
            "killer_name": killer_name, "status": "active", "crime_time": crime_time.isoformat(),
            "notebook": {"notes": "", "clues": {}},
            "proof": [f"{forensic_id}: {dna}",
                      f"{video_id}: câmera periciada identifica {killer_name} na Sala do Cofre às {crime_time:%H:%M}, no momento do homicídio.",
                      "Cruze o laudo com o registro visual e os depoimentos para compreender a solução do caso."]}

    from .sql_case import prepare_case
    case["sql_game"] = prepare_case(case)
    case["proof"] = case["sql_game"]["proof"]
    return case


def start_game() -> tuple[str, dict]:
    game_id = str(uuid4())
    with LOCK:
        state = {"active": generate_case(game_id, 1), "history": []}
        save_game(game_id, state)
    return game_id, state


def accuse(game_id: str, case_id: str, suspect_id: str) -> dict:
    with LOCK:
        state = load_game(game_id)
        case = state["active"]
        if case["id"] != case_id or case["status"] != "active":
            raise ValueError("Esta tentativa já foi usada. Atualize a página para abrir o caso atual.")
        suspects = pd.read_csv(Path(case["folder"]) / "raw" / "suspects.csv")
        if suspect_id not in suspects.suspect_id.tolist():
            raise ValueError("Selecione um suspeito válido.")
        correct = suspect_id == case["killer_id"]
        # Geração antes do commit: falha de pipeline não consome a tentativa.
        next_case = None if correct else generate_case(game_id, case["number"] + 1, case["killer_id"])
        closed = {**case, "status": "solved" if correct else "failed", "accused_id": suspect_id,
                  "accused_name": suspects.loc[suspects.suspect_id == suspect_id, "suspect_name"].iloc[0],
                  "closed_at": datetime.now().isoformat()}
        state["history"].insert(0, closed)
        state["active"] = closed if correct else next_case
        save_game(game_id, state)
        return state


def next_investigation(game_id: str, case_id: str) -> dict:
    with LOCK:
        state = load_game(game_id)
        case = state["active"]
        if case["id"] != case_id or case["status"] != "solved":
            raise ValueError("Conclua o caso ativo primeiro.")
        state["active"] = generate_case(game_id, case["number"] + 1, case["killer_id"])
        save_game(game_id, state)
        return state
