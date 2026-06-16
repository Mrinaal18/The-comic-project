
Inkverse — main Streamlit application.

A colorful, open-source collaborative storytelling platform where writers can:
  * Publish original stories & fan fiction (Problem 1)
  * Collaborate on shared fictional universes
  * Showcase short-film adaptations of their work
  * Run an AI copyright / originality check before publishing (Problem 2)
  * Read the platform's legal & IP guidance

Run locally:   streamlit run streamlit_app.py
Deploy:        push to GitHub -> Streamlit Community Cloud, set secrets.
"""

from __future__ import annotations

import streamlit as st

from lib import ui
from views import (
    page_home,
    page_explore,
    page_write,
    page_universes,
    page_films,
    page_copyright,
    page_legal,
    page_account,
)

st.set_page_config(
    page_title="Inkverse — stories, universes & short films",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

ui.inject_css()


PAGES = {
    "Home": page_home.render,
    "Explore stories": page_explore.render,
    "Write & publish": page_write.render,
    "Shared universes": page_universes.render,
    "Short films": page_films.render,
    "Copyright check": page_copyright.render,
    "Legal & IP": page_legal.render,
    "Account": page_account.render,
}


def sidebar() -> str:
    with st.sidebar:
        ui.brand_header()
        st.divider()

        user = st.session_state.get("user")
        if user:
            st.success(f"Signed in as **{user['display_name']}**")
        else:
            st.info("Browsing as a guest. Sign in to publish.")

        choice = st.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")

        st.divider()
        from lib import storage
        from lib.copyright_checker import ai_enabled

        st.caption("System status")
        st.write("Storage:", "GitHub" if storage.github_enabled() else "Local (demo)")
        st.write("AI checker:", "Enabled" if ai_enabled() else "Disabled")
        st.caption("Configure secrets to enable GitHub persistence & AI.")
    return choice


def main() -> None:
    choice = sidebar()
    PAGES[choice]()


if __name__ == "__main__":
    main()
