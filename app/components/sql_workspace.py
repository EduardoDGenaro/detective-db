"""Player-facing SQL workspace, schema dictionary and notebook."""
from pathlib import Path

import duckdb
import streamlit as st

from .case_game import save_notes
from .sql_case import TABLES, query_case

DESCRIPTIONS = {
    "laudo_vitima": "Necropsia: janela estimada da morte, local, causa e vestígios do agressor.",
    "testemunhas": "Pessoas investigadas: depoimentos, expediente, álibis declarados, acessos periciados e características das roupas.",
    "locais": "Contexto dos locais: tipo, acesso, movimentação e pessoas presentes no período registrado.",
}


def render_workspace(case: dict) -> None:
    st.write("Augusto Valmont foi assassinado. Investigue os dados e descubra qual depoimento não se sustenta diante do laudo e dos registros do local.")
    st.caption("Consulte → cruze os registros → anote sua hipótese → faça uma acusação. Você tem uma chance por caso.")
    editor, dictionary = st.columns([1.8, 1], gap="medium")
    with dictionary:
        st.subheader("Tabelas do caso")
        with duckdb.connect(str(Path(case["folder"]) / "sql" / "case.duckdb"), read_only=True) as db:
            for table in TABLES:
                with st.expander(table):
                    st.write(DESCRIPTIONS[table])
                    fields = db.execute(f'DESCRIBE "{table}"').fetchdf()[["column_name", "column_type"]]
                    fields.columns = ["Coluna", "Tipo"]
                    st.dataframe(fields, hide_index=True, width="stretch")
        with st.expander("Como interpretar os registros"):
            st.write("O álibi e o local declarado são afirmações da pessoa. Entrada, saída e local registrado vêm de acessos periciados. Horário do relato é o momento descrito; horário do depoimento é quando a polícia o coletou.")
            st.write("A quantidade de pessoas e a movimentação descrevem o intervalo inicio_registro–fim_registro. O expediente informa o turno de trabalho, não comprova um álibi.")
            st.write("Neste enigma, a conclusão exige presença durante toda a janela da morte, depoimento incompatível nesse horário e correspondência dos dois vestígios. Uma contradição sozinha não prova culpa.")
        with st.expander("Ajuda com SQL"):
            st.code("SELECT nome, profissao\nFROM testemunhas\nORDER BY nome;", language="sql")
            st.code("SELECT t.nome, l.nome AS local_declarado\nFROM testemunhas t\nJOIN locais l\n  ON t.local_declarado_id = l.local_id;", language="sql")
            st.caption("Use WHERE para filtrar, JOIN para cruzar tabelas e BETWEEN para comparar horários. Consultas com WITH também são aceitas.")
        st.caption("Relações: laudo_vitima.local_id e os campos local_declarado_id / local_registrado_id de testemunhas apontam para locais.local_id.")
    with editor:
        st.subheader("Console SQL")
        with st.form(f"sql_form_{case['id']}"):
            sql = st.text_area("Sua consulta", value=st.session_state.get(f"sql_result_{case['id']}", {}).get("sql", "SELECT * FROM laudo_vitima;"), height=170,
                               key=f"sql_editor_{case['id']}", max_chars=20000)
            run = st.form_submit_button("Executar consulta", type="primary")
        st.caption("DuckDB SQL · somente leitura · até 500 linhas por resultado · limite de 3 segundos")
        result_key = f"sql_result_{case['id']}"
        if run:
            try:
                result = query_case(case, sql)
                st.session_state[result_key] = {"sql": sql, "frame": result, "error": None}
            except (duckdb.Error, ValueError) as exc:
                st.session_state[result_key] = {"sql": sql, "error": str(exc)}
        result = st.session_state.get(result_key)
        if result:
            if result["error"]:
                st.error("A consulta não foi executada. Revise a mensagem e tente novamente; isso não consome sua acusação.")
                st.code(result["error"], language=None)
            else:
                frame = result["frame"]
                st.subheader("Resultado da consulta")
                if len(frame) > 500:
                    st.warning("Exibindo as primeiras 500 linhas. Refine a consulta para reduzir o resultado.")
                elif frame.empty:
                    st.info("Nenhuma linha encontrada. Revise os filtros ou teste outra hipótese.")
                else:
                    st.caption(f"{len(frame)} linha(s) retornada(s)")
                st.dataframe(frame.head(500), hide_index=True, width="stretch")
                with st.expander("SQL deste resultado"):
                    st.code(result["sql"], language="sql")
                if case["status"] == "active" and st.button("Guardar consulta no caderno"):
                    notes = case.get("notebook", {}).get("notes", "")
                    addition = "\n\nConsulta investigada:\n" + result["sql"]
                    try:
                        st.session_state["game"] = save_notes(st.session_state["game_id"], case["id"], notes + addition)
                        st.session_state.pop(f"sql_notes_{case['id']}", None)
                        st.success("Consulta adicionada ao caderno.")
                    except ValueError as exc:
                        st.error(str(exc))
        else:
            st.info("Comece executando a consulta do laudo. Abra as tabelas ao lado para conhecer as colunas disponíveis.")


def render_notes(case: dict) -> None:
    st.caption("Registre hipóteses, trechos de SQL e conclusões. O caderno acompanha o caso no histórico.")
    notes = case.get("notebook", {}).get("notes", "")
    if case["status"] != "active":
        st.info("Caso encerrado. Caderno preservado em modo de leitura.")
        st.text(notes or "Nenhuma anotação registrada.")
        return
    key = f"sql_notes_{case['id']}"
    if key not in st.session_state:
        st.session_state[key] = notes
    def persist():
        try:
            st.session_state["game"] = save_notes(st.session_state["game_id"], case["id"], st.session_state[key])
            st.session_state.pop("sql_notes_error", None)
        except (ValueError, OSError) as exc:
            st.session_state["sql_notes_error"] = str(exc)
    st.text_area("Anotações da investigação", key=key, height=360, max_chars=10000, on_change=persist)
    st.caption("Salvo ao sair do campo. Até 10.000 caracteres.")
    if st.button("Salvar anotações", type="primary"):
        persist()
        if not st.session_state.get("sql_notes_error"):
            st.success("Caderno salvo.")
    if st.session_state.get("sql_notes_error"):
        st.error(st.session_state["sql_notes_error"])
