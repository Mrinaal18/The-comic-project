"""
ui.py
=====
Shared UI helpers and the colorful, unique visual identity for Inkverse.

We inject custom CSS to push Streamlit beyond its default look: a warm,
multi-color gradient palette, rounded cards, badges, and lively headers — while
staying within a small, cohesive set of brand colors.
"""

from __future__ import annotations

import streamlit as st

# Brand palette (cohesive, ~5 colors): coral, teal, sunny yellow, ink, cream.
CORAL = "#FF5A5F"
TEAL = "#1FB6A6"
SUN = "#FFB400"
INK = "#1F2933"
CREAM = "#FFFDF7"

GENRES = [
    "Fantasy", "Science Fiction", "Mystery", "Romance", "Horror",
    "Adventure", "Drama", "Fan Fiction", "Poetry", "Historical",
]


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        :root {{
            --coral: {CORAL};
            --teal: {TEAL};
            --sun: {SUN};
            --ink: {INK};
            --cream: {CREAM};
        }}

        .stApp {{
            background:
                radial-gradient(1200px 500px at 110% -10%, rgba(31,182,166,0.12), transparent),
                radial-gradient(1000px 500px at -10% 0%, rgba(255,90,95,0.10), transparent),
                var(--cream);
        }}

        /* Brand wordmark */
        .ink-brand {{
            font-size: 2.0rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: linear-gradient(90deg, var(--coral), var(--sun), var(--teal));
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        }}
        .ink-tag {{ color: #6B7280; margin-top: -6px; font-size: 0.9rem; }}

        /* Section headers */
        .ink-h2 {{
            font-size: 1.5rem; font-weight: 800; color: var(--ink);
            border-left: 6px solid var(--coral); padding-left: 12px; margin: 8px 0 4px;
        }}

        /* Cards */
        .ink-card {{
            background: #ffffff;
            border: 1px solid #F0E6DA;
            border-radius: 18px;
            padding: 18px 20px;
            box-shadow: 0 6px 22px rgba(31,41,51,0.06);
            margin-bottom: 14px;
        }}
        .ink-card h4 {{ margin: 0 0 6px; color: var(--ink); font-size: 1.15rem; }}
        .ink-card p {{ margin: 0; color: #4B5563; }}

        /* Genre / status badges */
        .ink-badge {{
            display: inline-block; padding: 3px 12px; border-radius: 999px;
            font-size: 0.78rem; font-weight: 700; margin: 2px 6px 2px 0; color: #fff;
        }}
        .b-coral {{ background: var(--coral); }}
        .b-teal {{ background: var(--teal); }}
        .b-sun {{ background: var(--sun); color: var(--ink); }}
        .b-ink {{ background: var(--ink); }}

        /* Risk chips for the copyright checker */
        .risk {{ padding: 4px 14px; border-radius: 999px; font-weight: 800; color:#fff; }}
        .risk-none {{ background: var(--teal); }}
        .risk-low {{ background: #4CAF50; }}
        .risk-medium {{ background: var(--sun); color: var(--ink); }}
        .risk-high {{ background: var(--coral); }}

        /* Buttons */
        .stButton > button {{
            border-radius: 12px; font-weight: 700; border: 0;
        }}
        .stButton > button[kind="primary"] {{
            background: linear-gradient(90deg, var(--coral), var(--sun));
            color: #fff;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab"] {{ font-weight: 700; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def brand_header() -> None:
    st.markdown('<p class="ink-brand">Inkverse</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="ink-tag">A colorful, open home for original stories, fan fiction & their short-film adaptations.</p>',
        unsafe_allow_html=True,
    )


def section(title: str) -> None:
    st.markdown(f'<div class="ink-h2">{title}</div>', unsafe_allow_html=True)


def genre_badge(genre: str) -> str:
    colors = {0: "b-coral", 1: "b-teal", 2: "b-sun", 3: "b-ink"}
    cls = colors[hash(genre) % 4]
    return f'<span class="ink-badge {cls}">{genre}</span>'


def risk_chip(level: str) -> str:
    level = (level or "none").lower()
    label = {"none": "No risk", "low": "Low risk", "medium": "Medium risk", "high": "High risk"}.get(level, "Unknown")
    return f'<span class="risk risk-{level}">{label}</span>'
