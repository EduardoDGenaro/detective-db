"""DetectiveDB: investigue um homicídio consultando três tabelas com SQL."""
from pathlib import Path
import sys
import pandas as pd
import streamlit as st
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
from components.case_game import accuse, load_game, start_game, next_investigation, save_game, LOCK
from components.sql_case import CASE_VERSION, prepare_case, query_case
from components.sql_workspace import render_workspace, render_notes
from components.cards import render_header
from styles.theme import get_custom_css

st.set_page_config(page_title="DetectiveDB | Investigue com SQL", layout="wide", initial_sidebar_state="auto")
st.markdown(get_custom_css(), unsafe_allow_html=True)

def _format_timestamp(value):
    return pd.to_datetime(value).strftime("%d/%m/%Y · %H:%M")

def render_accusation_page(data: dict) -> None:
    state = st.session_state["game"]
    case = state["active"]
    if case["status"] == "solved":
        st.success(f"Caso encerrado. Você identificou {case['killer_name']} corretamente.")
        st.info("A solução e as provas estão na aba Histórico dos casos.")
        if st.button("Investigar novo caso", type="primary"):
            try:
                with st.spinner("Preparando outra investigação e validando as fontes…"):
                    st.session_state["game"] = next_investigation(st.session_state["game_id"], case["id"])
                st.session_state["current_page"] = "Investigar com SQL"
                st.session_state.pop("global_search", None)
                st.rerun()
            except (RuntimeError, ValueError, OSError) as exc:
                st.error(str(exc))
        return
    with st.container(border=True):
        st.subheader("Quem é o assassino?")
        st.caption(f"Homicídio de Augusto Valmont · {case['sql_game']['location']} · {_format_timestamp(case['sql_game']['crime_time'])}")
        st.write("Uma acusação por caso. Cruze o laudo, as testemunhas e os locais usando SQL antes de decidir.")
        st.warning("Se errar, este caso será encerrado e os dados serão randomizados. Outro suspeito será o assassino e a investigação recomeçará.")
        suspects = data["suspects"].sort_values("suspect_name")
        options = dict(zip(suspects.suspect_id, suspects.suspect_name))
        with st.form(f"accusation_{case['id']}"):
            selected = st.selectbox("Suspeito acusado", list(options), index=None,
                                    format_func=lambda value: options[value], placeholder="Selecione o suspeito…")
            understood = st.checkbox("Entendo que tenho apenas uma chance neste caso.")
            submitted = st.form_submit_button("Confirmar acusação", type="primary")
        if submitted:
            if not selected or not understood:
                st.error("Selecione um suspeito e confirme que compreendeu a regra da tentativa única.")
            else:
                try:
                    with st.spinner("Verificando a acusação e preparando os dados…"):
                        updated = accuse(st.session_state["game_id"], case["id"], selected)
                    st.session_state["game"] = updated
                    st.session_state["case_feedback"] = (
                        "Acusação correta! Veja a solução no histórico." if updated["active"]["status"] == "solved"
                        else "Acusação incorreta. O caso anterior foi arquivado com a solução. Um novo caso, com outro assassino, está pronto.")
                    st.session_state["current_page"] = "Histórico dos casos"
                    st.session_state.pop("global_search", None)
                    st.rerun()
                except (RuntimeError, ValueError, OSError) as exc:
                    st.error(str(exc))



def render_history_page():
    history = st.session_state["game"]["history"]
    if not history:
        st.info("Após sua primeira acusação, o caso anterior aparecerá aqui com o culpado, a explicação e seu caderno.")
    for index, case in enumerate(history):
        result = "Resolvido" if case["status"] == "solved" else "Acusação incorreta"
        with st.expander(f"Caso {case['number']:03d} · {result}", expanded=index == 0):
            st.write(f"Assassino: {case['killer_name']} · Sua acusação: {case['accused_name']}")
            for proof in case["proof"]:
                st.write(proof)
            if case.get("sql_game"):
                with st.expander("Consulta que demonstra a solução"):
                    st.code(case["sql_game"]["solution_sql"], language="sql")
            with st.expander("Caderno arquivado"):
                st.text(case.get("notebook", {}).get("notes") or "Nenhuma anotação registrada.")

def main():
    try:
        if "game_id" not in st.session_state:
            requested = st.query_params.get("partida", "")
            if requested:
                load_game(requested)
                st.session_state["game_id"] = requested
            else:
                with st.spinner("Preparando o mistério e validando as tabelas com dbt…"):
                    game_id, _ = start_game()
                st.session_state["game_id"] = game_id
                st.query_params["partida"] = game_id
        game_id = st.session_state["game_id"]
        state = load_game(game_id)
        if not state["active"].get("sql_game") or (
            state["active"]["status"] == "active"
            and state["active"]["sql_game"].get("version") != CASE_VERSION
        ):
            with st.spinner("Preparando as três tabelas desta investigação…"):
                with LOCK:
                    state = load_game(game_id)
                    state["active"]["sql_game"] = prepare_case(state["active"])
                    state["active"]["proof"] = state["active"]["sql_game"]["proof"]
                    save_game(game_id, state)
        st.session_state["game"] = state
    except (ValueError, FileNotFoundError):
        st.error("Partida não encontrada.")
        if st.button("Abrir nova partida"):
            st.query_params.clear()
            st.session_state.pop("game_id", None)
            st.rerun()
        return
    except Exception as exc:
        st.error(f"Não foi possível preparar o caso: {exc}")
        if st.button("Tentar novamente"):
            st.rerun()
        return
    case = state["active"]
    pages = {"Investigar com SQL": ":material/code:", "Caderno de investigação": ":material/edit_note:",
             "Fazer acusação": ":material/gavel:", "Histórico dos casos": ":material/history:"}
    page = st.session_state.get("current_page", "Investigar com SQL")
    if page not in pages:
        page = "Investigar com SQL"
        st.session_state["current_page"] = page
    with st.sidebar:
        mark = APP_DIR.parent / "assets" / "branding" / "detective_mark.png"
        if mark.exists():
            st.image(str(mark), width=72)
        st.markdown('<div class="brand-name">Detective<span>DB</span></div>', unsafe_allow_html=True)
        st.caption("UM MISTÉRIO PARA RESOLVER COM SQL")
        st.divider()
        st.caption(f"CASO {case['number']:03d} · MANSÃO VALMONT")
        for label, icon in pages.items():
            if st.button(label, key=f"nav_{label}", icon=icon, width="stretch", type="primary" if page == label else "secondary"):
                st.session_state["current_page"] = label
                st.rerun()
        st.divider()
        st.caption("3 tabelas. Uma acusação. Suas consultas conduzem a investigação.")
    render_header(page, f"Caso {case['number']:03d} · " + ("Em investigação" if case["status"] == "active" else "Encerrado"))
    if feedback := st.session_state.pop("case_feedback", None):
        st.info(feedback)
    if page == "Investigar com SQL":
        if case["status"] == "solved":
            st.success("Caso resolvido. Consulte a solução no histórico ou abra outro caso em Fazer acusação.")
        render_workspace(case)
    elif page == "Caderno de investigação":
        render_notes(case)
    elif page == "Fazer acusação":
        suspects = query_case(case, "SELECT pessoa_id AS suspect_id, nome AS suspect_name FROM testemunhas")
        render_accusation_page({"suspects": suspects})
    else:
        render_history_page()

if __name__ == "__main__":
    main()
