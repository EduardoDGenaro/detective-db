"""Leitura de dossiês, comparação de fontes e caderno do jogador."""
from __future__ import annotations

from html import escape
import pandas as pd
import streamlit as st

from .case_game import save_notes, pin_clue

KINDS = {"evidence": "Evidência", "testimony": "Depoimento", "camera": "Câmera"}


def timestamp(value) -> str:
    parsed = pd.to_datetime(value, errors="coerce")
    return "Horário não informado" if pd.isna(parsed) else parsed.strftime("%d/%m/%Y · %H:%M")


def camera_matches(testimony, cameras: pd.DataFrame, conflicts_only: bool = False) -> pd.DataFrame:
    """Mesma janela por fronteiras de minuto usada por date_diff no dbt."""
    claimed = pd.to_datetime(testimony["claimed_event_time"], errors="coerce")
    if pd.isna(claimed):
        return cameras.iloc[0:0]
    minute_delta = (pd.to_datetime(cameras["seen_at"]).dt.floor("min") - claimed.floor("min")).abs()
    mask = (cameras["suspect_id"] == testimony["suspect_id"]) & (minute_delta <= pd.Timedelta(minutes=5))
    if conflicts_only:
        mask &= cameras["location_id"].notna() & (cameras["location_id"] != testimony["claimed_location_id"])
    return cameras[mask].sort_values(["seen_at", "camera_event_id"])


def open_dossier(suspect_id: str) -> None:
    st.session_state["dossier_id"] = suspect_id
    st.session_state["dossier_open"] = True
    st.session_state["current_page"] = "Suspeitos"
    st.rerun()


def pin_button(kind: str, reference_id: str, context: str) -> None:
    case = st.session_state["game"]["active"]
    notebook = case.get("notebook", {"clues": {}})
    selected = f"{kind}:{reference_id}" in notebook.get("clues", {})
    if case["status"] != "active":
        if selected:
            st.caption("Marcada no caderno arquivado")
        return
    label = f"Desmarcar {reference_id}" if selected else f"Marcar {reference_id} no caderno"
    if st.button(label, key=f"pin_{case['id']}_{context}_{kind}_{reference_id}",
                 icon=":material/bookmark_added:" if selected else ":material/bookmark_add:"):
        try:
            st.session_state["game"] = pin_clue(st.session_state["game_id"], case["id"], kind, reference_id, not selected)
            st.rerun()
        except (ValueError, OSError) as exc:
            st.error(str(exc))


def comparison_card(row, cameras: pd.DataFrame, context: str, allow_open: bool = True) -> None:
    matches = camera_matches(row, cameras)
    conflict = bool(row["has_alibi_camera_conflict"])
    with st.container(border=True):
        title, action = st.columns([3, 1])
        with title:
            st.markdown(f"**{row['suspect_name']} · {row['testimony_id']}**")
            st.caption("Locais diferentes na mesma janela de tempo" if conflict else (
                "Registro compatível com o local declarado" if not matches.empty else "Sem câmera na janela de cinco minutos"))
        with action:
            if allow_open and st.button("Abrir dossiê", key=f"dossier_{context}_{row['testimony_id']}"):
                open_dossier(str(row["suspect_id"]))
        observations = []
        for _, camera in matches.iterrows():
            mismatch = camera["location_id"] != row["claimed_location_id"]
            observations.append(
                f"<div class='camera-observation'><strong>{escape(str(camera['camera_event_id']))} · "
                f"{escape(str(camera['camera_label']))}</strong><span>{timestamp(camera['seen_at'])}</span>"
                f"<p>{escape(str(camera['location_name']))}</p><small>"
                + ("Local diferente do declarado" if mismatch else "Mesmo local declarado") + "</small></div>"
            )
        if not observations:
            observations.append("<p class='comparison-empty'>Não há registro dessa pessoa na janela de cinco minutos. A ausência de imagem não confirma o álibi.</p>")
        st.html(
            "<div class='comparison-grid'><section class='comparison-source'><h4>O que declarou</h4>"
            f"<span>{timestamp(row['claimed_event_time'])}</span><p><strong>{escape(str(row['claimed_location_name']))}</strong></p>"
            f"<p>{escape(str(row['statement']))}</p></section><section class='comparison-source comparison-source--camera'>"
            "<h4>O que a câmera registrou</h4>" + "".join(observations) + "</section></div>"
        )
        pin_button("testimony", str(row["testimony_id"]), context)


def evidence_card(row, context: str) -> None:
    labels = {"ANALYZED": "Analisada", "COLLECTED": "Aguardando análise", "DISCARDED": "Descartada"}
    with st.container(border=True):
        st.markdown(f"**{row['evidence_id']} · {str(row['evidence_type']).replace('_', ' ').capitalize()}**")
        st.caption(f"{labels.get(row['status'], row['status'])} · {row['location_name']} · {timestamp(row['collected_at'])}")
        st.write(str(row["evidence_description"]))
        if row["status"] == "DISCARDED":
            st.caption("Pista descartada na perícia; permanece no dossiê para consulta.")
        pin_button("evidence", str(row["evidence_id"]), context)


def render_saved_clues(case: dict, readonly: bool = False) -> None:
    clues = case.get("notebook", {}).get("clues", {})
    if not clues:
        st.info("Nenhuma pista marcada neste caso.")
    for key, clue in clues.items():
        with st.container(border=True):
            st.markdown(f"**{KINDS.get(clue['kind'], 'Pista')} {clue['id']} · {clue['suspect_name']}**")
            st.caption(f"{clue['location']} · {timestamp(clue['time'])}")
            st.write(clue["detail"])
            if not readonly:
                if clue.get("suspect_id") and st.button("Abrir dossiê", key=f"notebook_open_{case['id']}_{key}"):
                    open_dossier(clue["suspect_id"])
                pin_button(clue["kind"], clue["id"], "notebook")


def _persist_notes(case_id: str, widget_key: str) -> None:
    try:
        st.session_state["game"] = save_notes(st.session_state["game_id"], case_id, st.session_state[widget_key])
        st.session_state.pop("notes_error", None)
    except (ValueError, OSError) as exc:
        st.session_state["notes_error"] = str(exc)


def render_notebook_page() -> None:
    case = st.session_state["game"]["active"]
    notebook = case.get("notebook", {"notes": "", "clues": {}})
    st.caption("Marque pistas nos dossiês e registre suas hipóteses aqui. O caderno é guardado com o caso quando você acusa.")
    notes_tab, clues_tab = st.tabs(["Minhas anotações", f"Pistas marcadas ({len(notebook.get('clues', {}))})"])
    with notes_tab:
        if case["status"] != "active":
            st.info("Caso encerrado. Este caderno está arquivado e não pode mais ser editado.")
            st.text(notebook.get("notes") or "Nenhuma anotação registrada.")
        else:
            key = f"notes_{case['id']}"
            if key not in st.session_state:
                st.session_state[key] = notebook.get("notes", "")
            st.text_area("Hipóteses e observações", key=key, height=240, max_chars=10000,
                         placeholder="O que chama sua atenção? Quais fontes ainda precisa comparar?",
                         on_change=_persist_notes, args=(case["id"], key))
            st.caption("Salvo automaticamente ao sair do campo. Até 10.000 caracteres.")
            if st.button("Salvar agora", key=f"save_notes_{case['id']}"):
                _persist_notes(case["id"], key)
                if not st.session_state.get("notes_error"):
                    st.success("Anotações salvas.")
            if st.session_state.get("notes_error"):
                st.error(st.session_state["notes_error"])
            saved_at = st.session_state["game"]["active"].get("notebook", {}).get("saved_at")
            if saved_at:
                st.caption(f"Último salvamento: {timestamp(saved_at)}")
    with clues_tab:
        render_saved_clues(case, readonly=case["status"] != "active")
