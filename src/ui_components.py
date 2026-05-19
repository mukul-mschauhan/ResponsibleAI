"""Reusable Streamlit UI helpers.

Professional light-theme replacement file.
Overwrite: src/ui_components.py
"""

from __future__ import annotations

from typing import Optional

import plotly.graph_objects as go
import streamlit as st


TEXT = "#111827"
MUTED = "#5B6475"
BORDER = "rgba(17, 24, 39, 0.10)"
GRID = "rgba(17, 24, 39, 0.08)"
PRIMARY = "#2563EB"
PRIMARY_2 = "#4F46E5"
GREEN = "#15803D"
AMBER = "#B45309"
RED = "#B91C1C"


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --rai-bg: #F7F9FC;
            --rai-surface: #FFFFFF;
            --rai-surface-soft: #F3F6FB;
            --rai-border: rgba(17, 24, 39, 0.10);
            --rai-text: #111827;
            --rai-muted: #5B6475;
            --rai-primary: #2563EB;
            --rai-primary-2: #4F46E5;
            --rai-green: #15803D;
            --rai-amber: #B45309;
            --rai-red: #B91C1C;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: var(--rai-text) !important;
            font-size: 15px;
        }

        .stApp,
        .main,
        section.main,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"] {
            background:
                radial-gradient(circle at 4% 0%, rgba(79,70,229,0.08), transparent 28%),
                radial-gradient(circle at 96% 0%, rgba(37,99,235,0.07), transparent 28%),
                linear-gradient(180deg, #FFFFFF 0%, #F7F9FC 52%, #F3F6FB 100%) !important;
            color: var(--rai-text) !important;
        }

        .block-container {
            padding-top: 1.15rem;
            padding-bottom: 2rem;
            max-width: 1260px;
        }

        [data-testid="stHeader"] {
            background: rgba(255,255,255,0.82) !important;
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(17, 24, 39, 0.06);
        }

        [data-testid="stSidebar"],
        [data-testid="stSidebar"] > div {
            background: linear-gradient(180deg, #FFFFFF 0%, #F7F9FC 100%) !important;
            color: var(--rai-text) !important;
            border-right: 1px solid var(--rai-border);
        }

        /* Typography reset: prevents oversized black text and low-contrast captions */
        h1, h2, h3, h4, h5, h6 {
            color: var(--rai-text) !important;
            letter-spacing: -0.025em;
            line-height: 1.15;
        }
        h1 { font-size: clamp(2.0rem, 3vw, 2.65rem) !important; font-weight: 800 !important; }
        h2 { font-size: clamp(1.55rem, 2.2vw, 2.05rem) !important; font-weight: 800 !important; }
        h3 { font-size: clamp(1.18rem, 1.7vw, 1.45rem) !important; font-weight: 750 !important; }
        p, li, label, .stMarkdown, .stCaption, [data-testid="stMarkdownContainer"] {
            color: var(--rai-muted) !important;
            font-size: 0.98rem;
            line-height: 1.55;
        }
        strong, b { color: var(--rai-text) !important; }

        .hero {
            padding: 1.65rem 1.75rem;
            border-radius: 24px;
            background:
                linear-gradient(135deg, rgba(37,99,235,0.10), rgba(79,70,229,0.08)),
                rgba(255,255,255,0.96);
            border: 1px solid rgba(17,24,39,0.08);
            box-shadow: 0 20px 55px rgba(17,24,39,0.08);
            margin-bottom: 1.15rem;
        }
        .hero h1 {
            font-size: clamp(2.1rem, 3.4vw, 3.0rem) !important;
            line-height: 1.04;
            margin: 0.45rem 0 0.65rem 0;
            font-weight: 800;
            color: var(--rai-text) !important;
        }
        .hero p {
            font-size: 1.0rem;
            color: var(--rai-muted) !important;
            max-width: 980px;
            margin: 0;
        }

        .pill {
            display: inline-flex;
            align-items: center;
            padding: 0.32rem 0.68rem;
            border-radius: 999px;
            background: #EEF4FF;
            border: 1px solid rgba(37,99,235,0.16);
            color: #1E3A8A !important;
            font-size: 0.78rem;
            font-weight: 700;
            margin-right: 0.38rem;
            margin-bottom: 0.4rem;
        }

        .glass-card {
            padding: 1.0rem;
            border-radius: 20px;
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(17,24,39,0.08);
            box-shadow: 0 14px 34px rgba(17,24,39,0.07);
        }

        .metric-card {
            min-height: 138px;
            padding: 1.05rem 1.15rem;
            border-radius: 22px;
            background: linear-gradient(180deg, #FFFFFF, #FAFBFF);
            border: 1px solid rgba(17,24,39,0.09);
            box-shadow: 0 16px 38px rgba(17,24,39,0.07);
            overflow-wrap: anywhere;
        }
        .metric-label {
            color: #687386 !important;
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            font-weight: 800;
            margin-bottom: 0.55rem;
        }
        .metric-value {
            font-size: clamp(1.32rem, 2.0vw, 1.78rem);
            line-height: 1.18;
            font-weight: 800;
            color: var(--rai-text) !important;
            margin-top: 0.15rem;
        }
        .metric-note,
        .small-muted {
            color: var(--rai-muted) !important;
            font-size: 0.88rem !important;
            line-height: 1.45 !important;
            margin-top: 0.55rem;
        }

        .status-pass { color: var(--rai-green) !important; font-weight: 800; }
        .status-warn { color: var(--rai-amber) !important; font-weight: 800; }
        .status-fail { color: var(--rai-red) !important; font-weight: 800; }

        /* Tabs: more compact, boardroom-style */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.55rem;
            border-bottom: 0 !important;
            margin-bottom: 1rem;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #FFFFFF !important;
            border-radius: 14px;
            padding: 0.54rem 0.82rem !important;
            border: 1px solid rgba(17,24,39,0.11);
            box-shadow: 0 7px 18px rgba(17,24,39,0.05);
            color: var(--rai-text) !important;
            min-height: 42px !important;
        }
        .stTabs [data-baseweb="tab"] p {
            color: var(--rai-text) !important;
            font-size: 0.93rem !important;
            font-weight: 650 !important;
            margin: 0 !important;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #2563EB, #4F46E5) !important;
            color: white !important;
            border-color: rgba(37,99,235,0.25) !important;
        }
        .stTabs [aria-selected="true"] p { color: white !important; }

        /* Light, readable data tables */
        div[data-testid="stDataFrame"] {
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(17,24,39,0.10);
            box-shadow: 0 12px 30px rgba(17,24,39,0.06);
            background: #FFFFFF !important;
        }
        div[data-testid="stDataFrame"] * {
            font-size: 0.92rem !important;
        }

        /* Inputs, widgets and buttons */
        input,
        textarea,
        [data-baseweb="input"] > div,
        [data-baseweb="select"] > div,
        [data-baseweb="textarea"] > div,
        div[data-testid="stNumberInput"] input {
            background: #FFFFFF !important;
            color: var(--rai-text) !important;
            border-color: rgba(17,24,39,0.16) !important;
        }
        [data-baseweb="select"] span,
        [data-baseweb="select"] div,
        [data-testid="stSelectbox"] div,
        [data-testid="stMultiSelect"] div,
        [data-testid="stSlider"] div {
            color: var(--rai-text) !important;
        }

        /* Buttons: force readable text across Streamlit versions.
           Streamlit often renders the button label inside a <p>; the global
           paragraph color rule can otherwise override the button color. */
        .stButton > button,
        .stButton > button:focus,
        .stButton > button:active,
        div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stFormSubmitButton"] button:focus,
        div[data-testid="stFormSubmitButton"] button:active,
        div[data-testid="stDownloadButton"] button,
        div[data-testid="stDownloadButton"] button:focus,
        div[data-testid="stDownloadButton"] button:active,
        button[kind="primary"],
        button[kind="secondary"],
        [data-testid="baseButton-primary"],
        [data-testid="baseButton-secondary"] {
            border-radius: 13px !important;
            border: 1px solid rgba(37,99,235,0.24) !important;
            background: linear-gradient(135deg, #2563EB 0%, #4F46E5 100%) !important;
            color: #FFFFFF !important;
            font-weight: 750 !important;
            box-shadow: 0 12px 26px rgba(37,99,235,0.18) !important;
            min-height: 2.75rem !important;
        }

        .stButton > button *,
        div[data-testid="stFormSubmitButton"] button *,
        div[data-testid="stDownloadButton"] button *,
        button[kind="primary"] *,
        button[kind="secondary"] *,
        [data-testid="baseButton-primary"] *,
        [data-testid="baseButton-secondary"] * {
            color: #FFFFFF !important;
            opacity: 1 !important;
            font-weight: 750 !important;
        }

        .stButton > button p,
        div[data-testid="stFormSubmitButton"] button p,
        div[data-testid="stDownloadButton"] button p,
        button[kind="primary"] p,
        button[kind="secondary"] p,
        [data-testid="baseButton-primary"] p,
        [data-testid="baseButton-secondary"] p {
            color: #FFFFFF !important;
            margin: 0 !important;
            font-size: 0.96rem !important;
            line-height: 1.2 !important;
        }

        .stButton > button:hover,
        div[data-testid="stFormSubmitButton"] button:hover,
        div[data-testid="stDownloadButton"] button:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover,
        [data-testid="baseButton-primary"]:hover,
        [data-testid="baseButton-secondary"]:hover {
            transform: translateY(-1px);
            border-color: rgba(30,64,175,0.38) !important;
            background: linear-gradient(135deg, #1D4ED8 0%, #4338CA 100%) !important;
            box-shadow: 0 16px 34px rgba(37,99,235,0.22) !important;
        }

        .stButton > button:disabled,
        div[data-testid="stFormSubmitButton"] button:disabled,
        div[data-testid="stDownloadButton"] button:disabled,
        button:disabled {
            background: linear-gradient(135deg, #93C5FD 0%, #A5B4FC 100%) !important;
            color: #FFFFFF !important;
            opacity: 0.92 !important;
            border-color: rgba(147,197,253,0.6) !important;
            box-shadow: 0 8px 18px rgba(37,99,235,0.12) !important;
            cursor: not-allowed !important;
        }

        .stButton > button:disabled *,
        div[data-testid="stFormSubmitButton"] button:disabled *,
        div[data-testid="stDownloadButton"] button:disabled *,
        button:disabled * {
            color: #FFFFFF !important;
            opacity: 1 !important;
        }

        [data-testid="stInfo"], [data-testid="stSuccess"], [data-testid="stWarning"], [data-testid="stError"], [data-testid="stAlert"] {
            border-radius: 16px !important;
            border: 1px solid rgba(17,24,39,0.08) !important;
            color: var(--rai-text) !important;
        }
        [data-testid="stAlert"] p,
        [data-testid="stInfo"] p,
        [data-testid="stSuccess"] p,
        [data-testid="stWarning"] p,
        [data-testid="stError"] p {
            color: var(--rai-text) !important;
            font-size: 0.96rem !important;
        }

        [data-testid="stExpander"],
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 18px !important;
        }
        hr { border-color: rgba(17,24,39,0.10) !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <div>
                <span class="pill">Banking AI Governance</span>
                <span class="pill">Fraud Detection</span>
                <span class="pill">Responsible AI</span>
                <span class="pill">Bahrain Client Demo</span>
            </div>
            <h1>Responsible AI Banking Control Tower</h1>
            <p>
                A business-facing simulator that shows how a bank detects card fraud while applying
                explainability, fairness monitoring, privacy controls, human oversight, auditability,
                and model monitoring before customer-impacting decisions are made.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_badge(risk: str) -> str:
    mapping = {
        "Low": "🟢 Low",
        "Medium": "🟡 Medium",
        "High": "🟠 High",
        "Critical": "🔴 Critical",
    }
    return mapping.get(risk, risk)


def _base_layout(height: int) -> dict:
    return {
        "height": height,
        "margin": dict(l=18, r=18, t=48, b=28),
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "#FFFFFF",
        "font": {"color": TEXT, "family": "Inter, Arial, sans-serif", "size": 12},
        "title": {"font": {"color": TEXT, "size": 16}},
        "legend": {"font": {"color": TEXT}},
    }


def style_plotly_chart(fig: go.Figure, height: int = 360, xaxis_range: Optional[list[float]] = None) -> go.Figure:
    """Apply a readable light theme to Plotly charts across the app."""
    fig.update_layout(**_base_layout(height))
    fig.update_xaxes(
        color=TEXT,
        gridcolor=GRID,
        zerolinecolor=GRID,
        linecolor=BORDER,
        tickfont={"color": TEXT, "size": 11},
        title_font={"color": MUTED, "size": 12},
    )
    fig.update_yaxes(
        color=TEXT,
        gridcolor=GRID,
        zerolinecolor=GRID,
        linecolor=BORDER,
        tickfont={"color": TEXT, "size": 11},
        title_font={"color": MUTED, "size": 12},
    )
    if xaxis_range is not None:
        fig.update_xaxes(range=xaxis_range)
    return fig


def fraud_gauge(score: float) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score * 100,
            number={"suffix": "%", "font": {"size": 34, "color": TEXT}},
            title={"text": "Fraud Risk Score", "font": {"size": 16, "color": TEXT}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": MUTED, "tickfont": {"color": TEXT, "size": 10}},
                "bar": {"color": PRIMARY_2},
                "bgcolor": "#FFFFFF",
                "borderwidth": 1,
                "bordercolor": BORDER,
                "steps": [
                    {"range": [0, 30], "color": "rgba(21,128,61,0.18)"},
                    {"range": [30, 60], "color": "rgba(180,83,9,0.16)"},
                    {"range": [60, 75], "color": "rgba(249,115,22,0.20)"},
                    {"range": [75, 100], "color": "rgba(185,28,28,0.20)"},
                ],
                "threshold": {"line": {"color": TEXT, "width": 3}, "thickness": 0.75, "value": score * 100},
            },
        )
    )
    fig.update_layout(**_base_layout(285))
    return fig


def scorecard_gauge(avg_score: float) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=avg_score,
            number={"suffix": "/100", "font": {"size": 32, "color": TEXT}},
            title={"text": "Responsible AI Readiness", "font": {"size": 16, "color": TEXT}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": MUTED, "tickfont": {"color": TEXT, "size": 10}},
                "bar": {"color": PRIMARY},
                "bgcolor": "#FFFFFF",
                "borderwidth": 1,
                "bordercolor": BORDER,
                "steps": [
                    {"range": [0, 60], "color": "rgba(185,28,28,0.18)"},
                    {"range": [60, 80], "color": "rgba(180,83,9,0.16)"},
                    {"range": [80, 100], "color": "rgba(21,128,61,0.18)"},
                ],
            },
        )
    )
    fig.update_layout(**_base_layout(275))
    return fig


def section_title(title: str, subtitle: str = "") -> None:
    st.markdown(f"### {title}")
    if subtitle:
        st.markdown(f"<p class='small-muted'>{subtitle}</p>", unsafe_allow_html=True)