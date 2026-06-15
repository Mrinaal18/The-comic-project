"""Write & publish stories (with optional originality check before publishing)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import streamlit as st

from lib import auth, storage, ui
from lib.copyright_checker import check_draft, ai_enabled


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _render_check_result(result: dict) -> None:
    if result.get("message"):
        st.info(result["message"])
    st.markdown(
        "Overall risk: " + ui.risk_chip(result.get("overall_risk", "none")),
        unsafe_allow_html=True,
    )
    for cand in result.get("candidates", []):
        analysis = cand.get("analysis", {})
        with st.expander(
            f"{cand.get('title')} — similarity {cand.get('similarity')} "
            f"({analysis.get('risk_level', 'low')} risk)"
        ):
            st.markdown(ui.risk_chip(analysis.get("risk_level", "low")), unsafe_allow_html=True)
            st.write(analysis.get("similarity_explanation", ""))
            if analysis.get("overlaps"):
                st.markdown("**Potential overlaps**")
                for o in analysis["overlaps"]:
                    st.markdown(f"- {o}")
            if analysis.get("common_tropes"):
                st.markdown("**Shared but non-infringing tropes**")
                for t in analysis["common_tropes"]:
                    st.markdown(f"- {t}")
            if analysis.get("recommendation"):
                st.success(analysis["recommendation"])


def render() -> None:
    ui.section("Write & publish")

    user = auth.current_user()
    if not user:
        st.warning("Please sign in from the Account page to write and publish.")
        return

    universes = storage.read_collection("universes")
    universe_names = ["(none — standalone story)"] + [u.get("name") for u in universes]

    st.caption("Your draft is saved to your account. You keep full creative control and rights.")

    title = st.text_input("Title")
    col1, col2 = st.columns(2)
    with col1:
        genres = st.multiselect("Genres", ui.GENRES)
    with col2:
        universe_choice = st.selectbox("Add to a shared universe?", universe_names)

    synopsis = st.text_area("Short synopsis (shown on cards)", height=80)
    body = st.text_area("Your story", height=360, placeholder="Once upon a time...")

    word_count = len((body or "").split())
    st.caption(f"Word count: {word_count}")

    st.divider()
    st.markdown("**Step 1 — Originality check (recommended before publishing)**")
    if not ai_enabled():
        st.info("AI checker is disabled. Add `openai_api_key` to secrets to enable it.")
    if st.button("Run originality check", disabled=not body):
        with st.spinner("Comparing your draft against the reference database..."):
            st.session_state["last_check"] = check_draft(body)
    if "last_check" in st.session_state:
        _render_check_result(st.session_state["last_check"])

    st.divider()
    st.markdown("**Step 2 — Save or publish**")
    c1, c2 = st.columns(2)

    def build_doc(status: str) -> dict:
        uni = None if universe_choice.startswith("(none") else universe_choice
        return {
            "id": uuid.uuid4().hex,
            "title": title.strip() or "Untitled",
            "author_id": user["id"],
            "author_name": user["display_name"],
            "genres": genres,
            "synopsis": synopsis.strip(),
            "body": body,
            "word_count": word_count,
            "universe_name": uni,
            "status": status,
            "created_at": _now(),
        }

    with c1:
        if st.button("Save as draft", use_container_width=True, disabled=not title):
            storage.append_document("stories", build_doc("draft"))
            st.success("Draft saved to your account.")
    with c2:
        if st.button("Publish", type="primary", use_container_width=True, disabled=not (title and body)):
            storage.append_document("stories", build_doc("published"))
            st.balloons()
            st.success("Published! Find it under Explore stories.")

    st.divider()
    ui.section("Your works")
    mine = storage.find_many("stories", author_id=user["id"])
    if not mine:
        st.caption("You have not created any works yet.")
    for s in sorted(mine, key=lambda x: x.get("created_at", ""), reverse=True):
        status_badge = (
            '<span class="ink-badge b-teal">Published</span>'
            if s.get("status") == "published"
            else '<span class="ink-badge b-sun">Draft</span>'
        )
        st.markdown(
            f'<div class="ink-card"><h4>{s.get("title")}</h4>'
            f'<p>{status_badge} · {s.get("word_count", 0)} words</p></div>',
            unsafe_allow_html=True,
        )
        if s.get("status") == "draft":
            if st.button("Publish this draft", key=f"pub-{s['id']}"):
                storage.update_document("stories", s["id"], {"status": "published"})
                st.success("Published.")
                st.rerun()
