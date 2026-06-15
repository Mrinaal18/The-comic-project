"""Home / landing page."""

from __future__ import annotations

import os

import streamlit as st

from lib import storage, ui


def _stat(label: str, value) -> None:
    st.markdown(
        f"""<div class="ink-card" style="text-align:center;">
        <h4 style="font-size:1.9rem;margin:0;">{value}</h4>
        <p>{label}</p></div>""",
        unsafe_allow_html=True,
    )


def render() -> None:
    col_text, col_img = st.columns([1.1, 1], vertical_alignment="center")
    with col_text:
        ui.brand_header()
        st.write("")
        st.markdown(
            "#### Where bold new stories find their readers — and their screens."
        )
        st.write(
            "Inkverse is an open, collaborative home for original fiction and fan "
            "fiction. Publish without gatekeepers, build shared fictional universes "
            "with other writers, showcase short-film adaptations of your work, and "
            "protect your ideas with a built-in AI originality check."
        )
        c1, c2 = st.columns(2)
        with c1:
            st.button("Start writing", type="primary", use_container_width=True,
                      help="Go to Write & publish from the sidebar.")
        with c2:
            st.button("Explore stories", use_container_width=True,
                      help="Open Explore stories from the sidebar.")
    with col_img:
        if os.path.exists("assets/hero.png"):
            st.image("assets/hero.png", use_container_width=True)

    st.write("")
    ui.section("Why Inkverse exists")
    p1, p2 = st.columns(2)
    with p1:
        st.markdown(
            """<div class="ink-card">
            <h4>Problem 1 — No platform to publish</h4>
            <p>Only ~1% of submitted drafts get published, and ~1% of those
            succeed. Self-publishing is costly and goes largely unread. Writers
            risk losing creative control. Inkverse gives every writer a stage and
            keeps their rights with them.</p></div>""",
            unsafe_allow_html=True,
        )
    with p2:
        st.markdown(
            """<div class="ink-card">
            <h4>Problem 2 — Accidental copyright issues</h4>
            <p>With millions of published works, new writers can't possibly check
            them all. Inkverse runs an AI originality check that flags overlapping
            plot points before you publish — protecting both new and established
            authors.</p></div>""",
            unsafe_allow_html=True,
        )

    st.write("")
    ui.section("Inkverse at a glance")
    stories = storage.read_collection("stories")
    films = storage.read_collection("films")
    universes = storage.read_collection("universes")
    users = storage.read_collection("users")

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        _stat("Stories", len([s for s in stories if s.get("status") == "published"]))
    with s2:
        _stat("Shared universes", len(universes))
    with s3:
        _stat("Short films", len(films))
    with s4:
        _stat("Writers", len(users))

    st.write("")
    ui.section("How it works")
    h1, h2, h3 = st.columns(3)
    steps = [
        ("1. Create an account", "Sign up in seconds. Your works stay yours."),
        ("2. Write or collaborate", "Publish solo or join a shared universe with other authors."),
        ("3. Check & publish", "Run the AI originality check, then share — and add film adaptations."),
    ]
    for col, (title, body) in zip([h1, h2, h3], steps):
        with col:
            st.markdown(
                f'<div class="ink-card"><h4>{title}</h4><p>{body}</p></div>',
                unsafe_allow_html=True,
            )
