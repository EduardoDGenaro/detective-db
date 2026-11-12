"""Tokens e overrides visuais da interface DetectiveDB."""

from __future__ import annotations

import base64
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _image_data_uri(relative_path: str) -> str:
    image_path = PROJECT_ROOT / "assets" / relative_path
    if not image_path.is_file():
        return ""
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def get_custom_css() -> str:
    sidebar_image = _image_data_uri("backgrounds/sidebar_scene.png")
    city_image = _image_data_uri("backgrounds/header_city.png")
    sidebar_layer = f", url('{sidebar_image}')" if sidebar_image else ""
    city_layer = f", url('{city_image}')" if city_image else ""
    return f"""
    <style>
        :root {{
            --bg-app: #080d12;
            --bg-sidebar: #0b0d11;
            --bg-panel: #111820;
            --bg-panel-alt: #151d26;
            --bg-hover: #1c2630;
            --border: #29333e;
            --text-primary: #f4f7fa;
            --text-secondary: #afbbc7;
            --text-muted: #82909d;
            --accent-red: #f05255;
            --accent-amber: #e9aa49;
            --accent-blue: #5aabe8;
            --accent-green: #3dcc78;
        }}

        html, body, [class*="css"] {{
            font-family: "Segoe UI Variable", "Bahnschrift", "Aptos", sans-serif;
            letter-spacing: 0;
            -webkit-font-smoothing: antialiased;
            text-rendering: optimizeLegibility;
            -webkit-text-size-adjust: 100%;
        }}
        .stApp {{
            color: var(--text-primary);
            background:
                radial-gradient(ellipse at 82% 0%, rgba(52, 67, 69, .16), transparent 42%),
                repeating-linear-gradient(135deg, rgba(255,255,255,.012) 0 1px, transparent 1px 9px),
                var(--bg-app);
        }}
            [data-testid="stHeader"], .stAppHeader {{ background: var(--bg-app); }}
        [data-testid="stAppViewContainer"] {{ background: transparent; }}
        [data-testid="stMainBlockContainer"] {{ max-width: 1540px; padding: 1.1rem 2rem 1.5rem; }}
        [data-testid="stMain"] [data-testid="stVerticalBlock"] {{ gap: .75rem; }}
        [data-testid="stSidebar"] {{
            background-color: var(--bg-sidebar);
            background-image: linear-gradient(180deg, #0b0d11 0%, rgba(11,13,17,.98) 50%, rgba(11,13,17,.54) 100%){sidebar_layer};
            background-size: cover;
            background-position: center bottom;
            border-right: 1px solid var(--border);
        }}
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap: .55rem; }}
        [data-testid="stSidebar"] [data-testid="stRadio"] label {{
            border-radius: 5px;
            padding: .5rem .65rem;
            color: var(--text-secondary);
            transition: background-color 140ms ease, color 140ms ease;
        }}
        [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{ background: var(--bg-hover); color: var(--text-primary); }}
        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {{
            background: rgba(240,82,85,.14);
            color: var(--text-primary);
            box-shadow: inset 2px 0 var(--accent-red);
        }}
        [data-testid="stSidebar"] hr {{ border-color: rgba(175,187,199,.12); }}
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{ color: var(--text-muted); }}
        [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {{
            background: rgba(240,82,85,.14) !important;
            border-color: rgba(240,82,85,.32) !important;
            box-shadow: inset 2px 0 var(--accent-red);
        }}
        .brand-name {{ color: var(--text-primary); font-size: 1.5rem; font-weight: 700; line-height: 1.1; }}
        .brand-name span {{ color: var(--accent-red); }}

        .case-header {{
            height: auto;
            min-height: 112px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: .3rem;
            padding: .5rem 1.2rem;
            border-left: 3px solid var(--accent-red);
            background-image: linear-gradient(90deg, rgba(8,13,18,.05), rgba(8,13,18,.18) 48%, #080d12 100%){city_layer};
            background-position: right 47%;
            background-size: cover;
            margin-bottom: .8rem;
        }}
        .case-header > p, .case-header > h1 {{ margin: 0 !important; }}
        .case-eyebrow {{ color: var(--accent-amber); font-size: .72rem; font-weight: 700; letter-spacing: .12em; margin: 0 0 .45rem; }}
        .case-title {{ color: var(--text-primary); font-size: 1.95rem; line-height: 1.15; font-weight: 700; margin: 0; }}
        .case-subtitle {{ display: flex; align-items: center; flex-wrap: wrap; gap: .55rem; color: var(--text-secondary); font-size: .88rem; margin: 0; }}
        .case-status {{ color: #ff9295; background: rgba(240,82,85,.14); border: 1px solid rgba(240,82,85,.28); border-radius: 999px; padding: .18rem .55rem; font-size: .72rem; white-space: nowrap; }}
        
        .kpi-card--red {{ --kpi-accent: var(--accent-red); background: linear-gradient(145deg, rgba(240,82,85,.11), rgba(17,24,32,.96) 76%); }}
        .kpi-card--amber {{ --kpi-accent: var(--accent-amber); background: linear-gradient(145deg, rgba(233,170,73,.11), rgba(17,24,32,.96) 76%); }}
        .kpi-card--blue {{ --kpi-accent: var(--accent-blue); background: linear-gradient(145deg, rgba(90,171,232,.11), rgba(17,24,32,.96) 76%); }}
        .kpi-card--green {{ --kpi-accent: var(--accent-green); background: linear-gradient(145deg, rgba(61,204,120,.11), rgba(17,24,32,.96) 76%); }}
        
        .material-symbols-rounded {{ font-family: "Material Symbols Rounded"; font-weight: normal; font-style: normal; font-size: 26px; line-height: 1; font-variation-settings: "FILL" 0, "wght" 500, "GRAD" 0, "opsz" 24; }}
        
        
        
        
        .stApp h2.section-title {{ color: var(--text-primary); font-size: 1.05rem !important; line-height: 1.3; font-weight: 650; margin: 0; }}
        .section-kicker {{ color: var(--text-muted); font-size: .75rem; margin: .2rem 0 .8rem; }}
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background: rgba(17,24,32,.88);
            border-color: var(--border) !important;
            border-radius: 6px !important;
        }}
        .suspect-table {{ width: 100%; border-collapse: collapse; table-layout: auto; font-size: .82rem; }}
        .stApp .suspect-table th {{ color: var(--text-muted); font-size: .7rem; font-weight: 650; text-align: left; padding: .55rem .35rem; border: 0 !important; border-bottom: 1px solid var(--border) !important; }}
        .stApp .suspect-table td {{ color: var(--text-secondary); vertical-align: middle; padding: .3rem .35rem; border: 0 !important; border-bottom: 1px solid rgba(41,51,62,.68) !important; }}
        .stApp .suspect-table tr:last-child td {{ border-bottom: 0 !important; }}
        .rank-index {{ display: inline-grid; place-items: center; width: 25px; height: 25px; color: var(--text-primary); background: #222c35; border-radius: 7px; font-size: .75rem; font-weight: 700; }}
        .suspect-identity {{ display: flex; align-items: center; gap: .5rem; }}
        .suspect-avatar {{ width: 28px; height: 28px; flex: 0 0 28px; display: grid; place-items: center; color: var(--text-secondary); background: #28323c; border-radius: 50%; font-size: .67rem; font-weight: 700; }}
        .suspect-name {{ color: var(--text-primary); font-weight: 600; }}
        .status-chip {{ display: inline-block; border-radius: 999px; padding: .22rem .48rem; font-size: .68rem; white-space: nowrap; }}
        .status-chip--danger {{ color: #ff9295; background: rgba(240,82,85,.14); }}
        .status-chip--warning {{ color: #f2c16f; background: rgba(233,170,73,.13); }}
        .status-chip--neutral {{ color: #bcc9d6; background: rgba(130,150,165,.12); }}
        .evidence-item {{ display: flex; align-items: center; gap: .8rem; padding: .7rem 0; border-bottom: 1px solid rgba(41,51,62,.68); }}
        .evidence-item:last-child {{ border-bottom: 0; }}
        .evidence-thumb {{ width: 105px; height: 64px; flex: 0 0 105px; object-fit: cover; border-radius: 5px; background: #202a34; }}
        .evidence-copy {{ min-width: 0; flex: 1; }}
        .evidence-title {{ color: var(--text-primary); font-size: .84rem; font-weight: 600; line-height: 1.3; }}
        .evidence-meta {{ color: var(--text-muted); font-size: .75rem; line-height: 1.4; margin-top: .22rem; }}
        .evidence-status {{ display: inline-block; color: var(--text-secondary); background: rgba(130,150,165,.12); border-radius: 999px; padding: .2rem .48rem; font-size: .7rem; white-space: nowrap; }}
        .summary-number {{ font-size: 2.55rem; line-height: 1; font-weight: 700; color: var(--accent-red); margin: .8rem 0 .5rem; }}
        .summary-copy {{ color: var(--text-secondary); font-size: .84rem; line-height: 1.5; }}
        .quality-layout {{ display: flex; align-items: center; gap: 1.1rem; padding-top: .5rem; }}
        .quality-ring {{
            width: 94px; height: 94px; flex: 0 0 94px; border-radius: 50%; display: grid; place-items: center;
            background: conic-gradient(var(--accent-green) calc(var(--rate) * 1%), #29333e 0);
            position: relative;
        }}
        .quality-ring::before {{ content: ""; position: absolute; inset: 8px; border-radius: 50%; background: var(--bg-panel); }}
        .quality-ring span {{ position: relative; color: var(--text-primary); font-size: 1.05rem; font-weight: 700; }}
        .quality-stats {{ display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: .65rem; width: 100%; }}
        .quality-stat strong {{ display: block; color: var(--text-primary); font-size: 1.1rem; }}
        .quality-stat span {{ color: var(--text-muted); font-size: .7rem; }}
        .methodology-notice {{ display: flex; flex-direction: column; gap: .25rem; color: var(--text-secondary); font-size: .78rem; line-height: 1.45; padding: .65rem .8rem; border-left: 2px solid var(--accent-amber); background: rgba(233,170,73,.07); margin: .6rem 0 .85rem; }}
        .methodology-notice strong {{ color: var(--accent-amber); font-size: .69rem; letter-spacing: .06em; }}
        .badge {{ display: inline-block; border-radius: 999px; padding: .2rem .55rem; font-size: .7rem; font-weight: 650; }}
        .badge-alert {{ color: #ff9295; background: rgba(240,82,85,.14); }}
        .badge-ok {{ color: #70e1a0; background: rgba(61,204,120,.13); }}
        .badge-amber {{ color: #f2c16f; background: rgba(233,170,73,.13); }}
        .badge-info {{ color: #8bc6f2; background: rgba(90,171,232,.13); }}
        .conflict-alert-item {{ color: var(--text-primary); background: rgba(240,82,85,.07); border: 1px solid var(--border); border-left: 3px solid var(--accent-red); padding: .8rem 1rem; border-radius: 5px; margin-bottom: .65rem; line-height: 1.65; }}
        [data-testid="stTextInput"] input, [data-testid="stSelectbox"] [data-baseweb="select"] > div {{ background: var(--bg-panel); border-color: var(--border); }}
        [data-testid="stTextInput"] input:focus {{ border-color: var(--accent-blue); box-shadow: 0 0 0 1px var(--accent-blue); }}
        [data-testid="stButton"] button {{ min-height: 40px; border-radius: 5px; border-color: var(--border); color: var(--text-primary); background: var(--bg-panel-alt); }}
        [data-testid="stButton"] button:hover {{ border-color: var(--accent-red); color: var(--text-primary); background: var(--bg-hover); }}
        [data-testid="stDataFrame"] {{ border: 1px solid var(--border); border-radius: 5px; }}
        :focus-visible {{ outline: 0 !important; box-shadow: 0 0 0 2px var(--accent-blue) !important; }}
        [data-testid="stTextInput"] input {{ font-size: 16px; font-variant-numeric: tabular-nums; }}
        .kpi-value, .suspect-table {{ font-variant-numeric: tabular-nums; }}
        @media (min-width: 768px) {{
            [data-testid="stHeader"] {{ display: none; }}
            [data-testid="stMainBlockContainer"] {{ padding: 1.1rem 2rem 1.5rem; }}
        }}
        @media (max-width: 900px) {{
            [data-testid="stMainBlockContainer"] {{ padding: 1.35rem 1rem 2rem; }}
            .case-header {{ height: auto; min-height: 108px; }}
            .case-title {{ font-size: 1.65rem; }}
            .evidence-thumb {{ width: 88px; height: 60px; flex-basis: 88px; }}
            .stHorizontalBlock:has(.kpi-card) > [data-testid="stColumn"] {{ min-width: calc(50% - .4rem) !important; flex: 1 1 calc(50% - .4rem) !important; }}
            .stHorizontalBlock:has(.suspect-table) > [data-testid="stColumn"],
            .stHorizontalBlock:has(.quality-layout) > [data-testid="stColumn"] {{ min-width: 100% !important; flex: 1 1 100% !important; }}
        }}
        @media (max-width: 640px) {{
            [data-testid="stSidebar"] {{ background-image: none; }}
            .stHorizontalBlock {{ flex-wrap: wrap; gap: .7rem; }}
            .stHorizontalBlock > [data-testid="stColumn"] {{ min-width: 100% !important; flex: 1 1 100% !important; }}
            .case-header {{ min-height: 96px; padding-left: .85rem; }}
            .case-title {{ font-size: 1.4rem; }}
            .case-subtitle {{ font-size: .82rem; }}
            
            .quality-layout {{ flex-wrap: wrap; }}
            .quality-stats {{ min-width: 100%; }}
        }}

        /* Direção visual: painel noir da referência, com leitura de dados reais. */
        :root {{ --bg-app: #080c0e; --bg-panel: #101619; --bg-panel-alt: #151c20;
                 --border: #465057; --text-secondary: #d1d4d5; --text-muted: #a3aaaf;
                 --accent-red: #ff4d50; --accent-amber: #ffb546; --accent-green: #29ce68; }}
        .stApp {{ background: linear-gradient(180deg, rgba(7,12,15,.45), #080c0e 270px){city_layer};
                  background-size: 100% auto; background-repeat: no-repeat; background-color: #080c0e; }}
        [data-testid="stSidebar"] {{ width: 248px !important; min-width: 248px !important;
            background-image: linear-gradient(180deg, #100d0e 0%, rgba(9,11,12,.98) 47%, rgba(9,11,12,.14) 100%){sidebar_layer}; }}
        [data-testid="stSidebarUserContent"] {{ padding: 1rem 1.05rem; }}
        [data-testid="stSidebar"] [data-testid="stImage"] {{ display: flex; justify-content: center; }}
        .brand-name {{ text-align: center; font-size: 1.75rem; }}
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{ text-align: center; }}
        [data-testid="stSidebar"] [data-testid="stButton"] button {{ background: transparent; border: 0; min-height: 44px;
            border-radius: 10px; justify-content: flex-start; padding: .55rem .85rem; font-size: 1rem; }}
        [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {{
            background: linear-gradient(100deg, #6c2325, #441a1d) !important; box-shadow: none; border: 0 !important; }}
        .case-header {{ background: none; border: 0; padding: .25rem 0; min-height: 90px; margin-bottom: .3rem; }}
        .case-title {{ font-size: clamp(26px, 2.6vw, 40px); letter-spacing: -.025em; }}
        .case-title::before {{ content: ''; display: inline-block; width: 4px; height: .8em; background: var(--accent-red);
            margin-right: 14px; border-radius: 3px; }}
        .case-status {{ border-radius: 8px; color: #ff8c81; }}
        
        
        .material-symbols-rounded {{ font-family: 'Segoe UI Symbol', sans-serif; font-size: 34px; }}
        
        
        
        [data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 15px !important; background: linear-gradient(150deg, #171d20, #0c1114); }}
        [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {{ padding: .9rem; }}
        .stApp h2.section-title {{ font-size: 1.45rem !important; font-weight: 700; padding: 0 0 .7rem; }}
        .suspect-table {{ font-size: .95rem; }}
        .stApp .suspect-table th {{ font-size: .8rem; background: #1a2024; padding: .7rem .45rem; color: #f4f5f5; }}
        .stApp .suspect-table td {{ padding: .6rem .45rem; }}
        .suspect-avatar {{ border-radius: 8px; width: 34px; height: 34px; flex-basis: 34px; }}
        .rank-index {{ border-radius: 8px; width: 30px; height: 30px; }}
        .status-chip {{ font-size: .73rem; border-radius: 8px; white-space: normal; }}
        .evidence-thumb {{ width: 108px; height: 68px; flex-basis: 108px; border-radius: 8px; }}
        .evidence-title {{ font-size: .94rem; }}
        .evidence-meta {{ font-size: .77rem; }}
        .evidence-status {{ color: #ffd28a; background: #4a3518; border-radius: 10px; }}
        .summary-number {{ font-size: 44px; }}
        .summary-copy {{ font-size: 1rem; }}
        .quality-ring {{ width: 140px; height: 140px; flex-basis: 140px; }}
        .quality-ring::before {{ inset: 16px; }}
        .quality-ring span {{ font-size: 1.8rem; }}
        .quality-stats {{ display: flex; flex-direction: column; gap: .5rem; }}
        .quality-stat {{ display: flex; justify-content: space-between; border-bottom: 1px solid #30383c; padding-bottom: .4rem; }}
        .quality-stat strong {{ order: 1; font-size: 1rem; }}
        .quality-stat span {{ font-size: .9rem; }}
        .methodology-notice, .conflict-alert-item {{ border-left: 0; border-radius: 8px; }}
        [data-testid="stTextInput"] > div {{ border-radius: 12px; }}
        [data-testid="stFormSubmitButton"] button {{ min-height: 44px; }}
        @media (max-width: 1100px) {{
            .evidence-item {{ flex-wrap: wrap; }}
            .evidence-status {{ margin-left: auto; }}
            .suspect-table {{ font-size: .8rem; }}
            .quality-ring {{ width: 110px; height: 110px; flex-basis: 110px; }}
        }}
        @media (max-width: 640px) {{
            .case-title {{ font-size: 26px; }}
            .case-subtitle {{ font-size: .8rem; }}
            
            .suspect-table {{ table-layout: fixed; font-size: .75rem; }}
            .suspect-table th:first-child {{ width: 30px; }}
            .suspect-avatar, .suspect-table .evidence-meta {{ display: none; }}
            .status-chip {{ font-size: .65rem; padding: .2rem; }}
            .quality-layout {{ flex-wrap: nowrap; }}
            .quality-stats {{ min-width: 0; }}
        }}
        @media (prefers-reduced-motion: reduce) {{ *, *::before, *::after {{ animation: none !important; transition: none !important; }} }}
        ::selection {{ background: #8b3338; color: white; }}

        .stApp, .stApp input, .stApp button, .stApp textarea {{ font-family: 'Segoe UI', sans-serif; }}
        .st-key-overview_suspects, .st-key-overview_evidence, .st-key-overview_conflicts, .st-key-overview_quality {{
            background: linear-gradient(145deg, #171d20, #0b1013); border: 1px solid #495259 !important;
            border-radius: 15px; padding: 1rem; }}
        .st-key-overview_conflicts {{ border-color: #a83c3e !important; }}
        
        
        
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap: .25rem; }}
        [data-testid="stSidebar"] [data-testid="stButton"] button {{ width: 100%; }}
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{ font-size: .65rem; letter-spacing: .035em; }}
        [data-testid="stSidebar"] [data-testid="stImage"] img {{ width: 76px; height: 64px; object-fit: cover; }}
        [data-testid="stSidebar"] hr {{ margin: .6rem 0; }}
        @media (min-width: 768px) {{
            [data-testid="stSidebarHeader"] {{ height: 0; min-height: 0; }}
            [data-testid="stSidebarUserContent"] {{ margin-top: 0; }}
            [data-testid="stMainBlockContainer"] {{ padding-top: .8rem; }}
        }}
        @media (max-width: 640px) {{
            .st-key-overview_suspects, .st-key-overview_evidence, .st-key-overview_conflicts, .st-key-overview_quality {{ padding: .7rem; }}
        }}

        .brand-name {{ margin: .2rem 0 .6rem; }}
        [data-testid="stSidebar"] {{ background-image: linear-gradient(180deg, #100d0e 0%, rgba(9,11,12,.96) 55%, rgba(9,11,12,.65) 75%, rgba(9,11,12,.2) 100%){sidebar_layer}; }}
        .stApp .suspect-table td {{ padding: .55rem .45rem; }}

        .stApp h1.case-title {{ font-size: clamp(26px, 2.6vw, 40px) !important; padding: 0 !important; }}
        [data-testid="stHorizontalBlock"] {{ gap: 1rem; }}
        @media (max-width: 640px) {{
            .stApp h1.case-title {{ font-size: 26px !important; }}
            [data-testid="stHorizontalBlock"] {{ flex-wrap: wrap; gap: 1rem; }}
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{ min-width: 100% !important; flex: 1 1 100% !important; }}
            
        }}



        [data-testid="stSidebar"][data-collapsed="true"] {{ min-width: 0 !important; width: 0 !important; }}
        @media (min-width: 768px) {{
            body:has([data-testid="stSidebar"][data-collapsed="true"]) [data-testid="stHeader"] {{
                display: flex !important; width: 50px; background: transparent; }}
            body:has([data-testid="stSidebar"][data-collapsed="true"]) [data-testid="stAppDeployButton"],
            body:has([data-testid="stSidebar"][data-collapsed="true"]) [data-testid="stMainMenu"] {{ display: none; }}
        }}

        /* Cartões dimensionados pelo conteúdo; texto e números têm escalas próprias. */
        .kpi-card {{
            box-sizing: border-box; width: 100%; min-width: 0; min-height: 128px;
            display: flex; align-items: flex-start; gap: 1rem; padding: 1.2rem;
            border: 1px solid var(--kpi-accent, var(--border)); border-radius: 14px;
        }}
        .kpi-icon {{
            box-sizing: border-box; display: grid; place-items: center;
            width: 50px; height: 50px; flex: 0 0 50px; border-radius: 14px;
            color: var(--kpi-accent); background: color-mix(in srgb, var(--kpi-accent) 15%, transparent);
        }}
        .kpi-content {{ flex: 1; min-width: 0; display: flex; flex-direction: column; gap: .4rem; }}
        .kpi-label {{ color: var(--text-secondary); font-size: .78rem; font-weight: 600; line-height: 1.4; overflow-wrap: break-word; }}
        .kpi-value {{ color: var(--text-primary); font-weight: 700; line-height: 1.2; margin: 0; overflow-wrap: break-word; }}
        .kpi-card--metric .kpi-value {{ font-size: clamp(28px, 2.5vw, 40px); }}
        .kpi-card--text .kpi-value {{ font-size: 1.3rem; line-height: 1.3; text-wrap: pretty; }}
        .kpi-sub {{ color: var(--text-muted); font-size: .75rem; line-height: 1.5; overflow-wrap: anywhere; }}
        [data-testid="stMainBlockContainer"] {{ container-type: inline-size; container-name: workspace; }}
        @container workspace (max-width: 1000px) {{
            [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .kpi-card) {{ flex-wrap: wrap; }}
            [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .kpi-card) > [data-testid="stColumn"] {{
                flex: 1 1 calc(50% - .5rem) !important; min-width: calc(50% - .5rem) !important;
            }}
        }}
        @container workspace (max-width: 560px) {{
            [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .kpi-card) > [data-testid="stColumn"] {{
                flex: 1 1 100% !important; min-width: 100% !important;
            }}
        }}
        @media (max-width: 640px) {{
            .kpi-card {{ min-height: 128px; padding: 1rem; }}
            .kpi-card--text .kpi-value {{ font-size: 1.25rem; }}
        }}

        [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .kpi-card) {{ align-items: stretch; }}
        [data-testid="stColumn"]:has(.kpi-card) > [data-testid="stVerticalBlock"],
        [data-testid="stElementContainer"]:has(> [data-testid="stHtml"] .kpi-card),
        [data-testid="stHtml"]:has(> .kpi-card) {{ height: 100%; }}
        .kpi-card {{ height: 100%; }}

        /* Densidade e alinhamento dos painéis, sem reservar espaço artificial. */
        .kpi-card {{ padding: 1rem; align-items: center; }}
        .kpi-card--text {{ min-height: 140px; }}
        .kpi-card--text .kpi-value {{ font-size: 1.2rem; }}
        .kpi-content {{ gap: .3rem; }}
        .st-key-overview_conflicts, .st-key-overview_quality {{ box-sizing: border-box; height: 100%; }}
        [data-testid="stColumn"]:has(.st-key-overview_conflicts),
        [data-testid="stColumn"]:has(.st-key-overview_quality) {{ display: flex; flex-direction: column; }}
        [data-testid="stColumn"]:has(.st-key-overview_conflicts) > [data-testid="stVerticalBlock"],
        [data-testid="stColumn"]:has(.st-key-overview_quality) > [data-testid="stVerticalBlock"] {{ flex: 1; }}
        [data-testid="stLayoutWrapper"]:has(> .st-key-overview_conflicts),
        [data-testid="stLayoutWrapper"]:has(> .st-key-overview_quality) {{ height: 100%; }}
        .conflict-preview {{ display: flex; flex-direction: column; gap: .2rem; padding: .6rem 0;
            border-top: 1px solid #30383c; font-size: .78rem; line-height: 1.45; }}
        .conflict-preview strong {{ color: var(--text-primary); font-size: .82rem; }}
        .conflict-preview span {{ color: var(--text-secondary); overflow-wrap: anywhere; }}
        .summary-number {{ margin: .25rem 0; }}
        .summary-copy {{ margin: .2rem 0; font-size: .9rem; }}
        .quality-ring {{ width: 112px; height: 112px; flex-basis: 112px; }}
        .quality-ring::before {{ inset: 12px; }}
        .quality-ring span {{ font-size: 1.6rem; }}
        .quality-layout {{ padding: .35rem 0; }}
        .st-key-overview_conflicts .section-title, .st-key-overview_quality .section-title {{ padding-bottom: .2rem !important; }}
        .suspect-table tr .rank-index {{ background: #283139; color: #d1d4d5; }}
        .suspect-table th:first-child {{ width: 34px; }}
        @media (max-width: 640px) {{
            .kpi-card, .kpi-card--text {{ min-height: 112px; }}
            .st-key-overview_conflicts, .st-key-overview_quality {{ height: auto; }}
            .quality-layout {{ align-items: center; }}
        }}

        .st-key-overview_suspects, .st-key-overview_evidence {{ height: 100%; box-sizing: border-box; }}
        [data-testid="stColumn"]:has(.st-key-overview_suspects),
        [data-testid="stColumn"]:has(.st-key-overview_evidence) {{ display: flex; flex-direction: column; }}
        [data-testid="stColumn"]:has(.st-key-overview_suspects) > [data-testid="stVerticalBlock"],
        [data-testid="stColumn"]:has(.st-key-overview_evidence) > [data-testid="stVerticalBlock"] {{ flex: 1; }}
        [data-testid="stLayoutWrapper"]:has(> .st-key-overview_suspects),
        [data-testid="stLayoutWrapper"]:has(> .st-key-overview_evidence) {{ height: 100%; }}
        .suspect-id {{ color: var(--text-muted); font-size: .75rem; font-variant-numeric: tabular-nums; }}
        .suspect-table th:first-child {{ width: 48px; }}
        @media (max-width: 640px) {{
            .st-key-overview_suspects, .st-key-overview_evidence {{ height: auto; }}
            .suspect-table th:first-child {{ width: 38px; }}
            .suspect-id {{ font-size: .65rem; }}
        }}

        /* Fontes comparáveis dentro do mesmo dossiê. */
        .comparison-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; }}
        .comparison-source {{ min-width: 0; padding: 1rem; background: #171e22; border-radius: 10px;
            border: 1px solid #344048; overflow-wrap: anywhere; }}
        .comparison-source--camera {{ background: #101c24; border-color: #355167; }}
        .stApp .comparison-source h4 {{ font-size: 1rem; margin: 0 0 .7rem; padding: 0; color: #f4f7fa; }}
        .comparison-source p {{ color: #d1d4d5; font-size: .9rem; line-height: 1.55; margin: .4rem 0; }}
        .comparison-source span, .comparison-source small {{ display: block; font-size: .78rem; color: #b1bcc4; }}
        .camera-observation {{ padding: .55rem 0; border-bottom: 1px solid #344048; }}
        .camera-observation:first-of-type {{ padding-top: 0; }}
        .camera-observation:last-child {{ border-bottom: 0; padding-bottom: 0; }}
        .camera-observation strong {{ font-size: .88rem; color: #9bd2f7; }}
        .st-key-overview_notebook {{ box-sizing: border-box; height: 100%; padding: 1rem;
            background: linear-gradient(145deg, #171d20, #0b1013); border: 1px solid #495259 !important; border-radius: 15px; }}
        [data-testid="stColumn"]:has(.st-key-overview_notebook) {{ display: flex; flex-direction: column; }}
        [data-testid="stColumn"]:has(.st-key-overview_notebook) > [data-testid="stVerticalBlock"] {{ flex: 1; }}
        [data-testid="stLayoutWrapper"]:has(> .st-key-overview_notebook) {{ height: 100%; }}
        .st-key-overview_suspects [data-testid="stButton"] button {{ justify-content: flex-start; text-align: left; }}
        [data-testid="stTextArea"] textarea {{ font-size: 16px; line-height: 1.6; }}
        [data-testid="stTabs"] [role="tablist"] {{ overflow-x: auto; gap: .65rem; }}
        [data-testid="stTabs"] [role="tab"] {{ white-space: nowrap; min-height: 44px; flex-shrink: 0; }}
        @container workspace (max-width: 700px) {{
            .comparison-grid {{ grid-template-columns: minmax(0, 1fr); }}
        }}
        @media (max-width: 640px) {{
            .st-key-overview_notebook {{ height: auto; padding: .7rem; }}
            .comparison-source {{ padding: .8rem; }}
            .comparison-grid {{ gap: .7rem; }}
        }}

        @container workspace (min-width: 701px) {{
            [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(3)):not(:has(> [data-testid="stColumn"]:nth-child(4))):has(.kpi-card) > [data-testid="stColumn"] {{
                flex: 1 1 0 !important; min-width: 0 !important;
            }}
        }}
        @container workspace (max-width: 700px) {{
            [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(3)):not(:has(> [data-testid="stColumn"]:nth-child(4))):has(.kpi-card) > [data-testid="stColumn"] {{
                flex: 1 1 100% !important; min-width: 100% !important;
            }}
        }}
        [data-testid="stForm"] textarea {{ font-family: Consolas, "Courier New", monospace; }}
        [data-testid="stFormSubmitButton"] button {{ background: #a92d32; border-color: #d94b50; }}
        [data-testid="stFormSubmitButton"] button:hover {{ background: #bf383e; }}
        @media (max-width: 900px) {{
            [data-testid="stMainBlockContainer"] {{ padding-top: 4.5rem !important; }}
            [data-testid="stAppDeployButton"], #MainMenu {{ display: none; }}
        }}
    </style>
    """

