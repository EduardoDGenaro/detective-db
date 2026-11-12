"""
Componentes visuais reutilizaveis para o painel Streamlit do DetectiveDB.
Implementa cartoes de KPI, cabecalhos e avisos metodologicos sem uso de emojis.
"""

from __future__ import annotations

import streamlit as st
from html import escape
import re
import base64


def render_header(title: str, subtitle: str) -> None:
    context, separator, status = subtitle.rpartition(" · ")
    subtitle_html = (
        f"{escape(context)}<span class='case-status'>{escape(status)}</span>"
        if separator and status == "Em investigação"
        else escape(subtitle)
    )
    st.markdown(
        f"""
        <div class="case-header">
            <h1 class="case-title">{escape(title)}</h1>
            <p class="case-subtitle">{subtitle_html}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(
    label: str,
    value: str | int,
    subtitle: str = "",
    tone: str = "amber",
) -> None:
    safe_label = escape(str(label))
    safe_value = escape(str(value))
    # Nomes e estados precisam de uma escala diferente dos indicadores numéricos.
    value_kind = "metric" if re.fullmatch(r"[\d.,%/\s+−-]+", str(value).strip()) else "text"
    sub_html = f'<div class="kpi-sub">{escape(str(subtitle))}</div>' if subtitle else ""
    label_key = str(label).lower()
    if "suspeit" in label_key:
        icon = '<circle cx="9" cy="7" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3z"/><circle cx="18" cy="8" r="2"/><path d="M18 13a5 5 0 0 1 5 5v3h-5"/>'
    elif "evid" in label_key:
        icon = '<path d="M3 5h7l2 3h9v13H3z"/>'
    elif "contrad" in label_key or "falh" in label_key or "álibi" in label_key:
        icon = '<path d="M12 3L2 21h20zM12 9v5m0 3v1"/>'
    elif "test" in label_key or "qualidade" in label_key:
        icon = '<path d="M12 3L2 8l10 5 10-5zM2 13l10 5 10-5M2 18l10 5 10-5"/>'
    else:
        icon = '<circle cx="12" cy="13" r="10"/><path d="M12 12v6m0-11v1"/>'
    icon_color = {"red": "#ff4d50", "amber": "#ffb546", "blue": "#5aabe8", "green": "#29ce68"}.get(tone, "#ffb546")
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 26" fill="none" stroke="{icon_color}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round">{icon}</svg>'
    icon_uri = "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode("ascii")
    st.html(
        f"""
        <div class="kpi-card kpi-card--{escape(tone)} kpi-card--{value_kind}">
            <div class="kpi-icon" aria-hidden="true"><img src="{icon_uri}" width="34" height="34" alt=""></div>
            <div class="kpi-content">
                <div class="kpi-label">{safe_label}</div>
                <div class="kpi-value">{safe_value}</div>
                {sub_html}
            </div>
        </div>
        """,
    )


def render_methodology_notice(text: str) -> None:
    st.markdown(
        f"""
        <div class="methodology-notice">
            <strong>NOTA METODOLÓGICA</strong><span>{escape(text)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_badge(text: str, variant: str = "info") -> str:
    variant_class = {
        "alert": "badge-alert",
        "ok": "badge-ok",
        "amber": "badge-amber",
        "info": "badge-info",
    }.get(variant, "badge-info")
    return f'<span class="badge {variant_class}">{escape(text)}</span>'

