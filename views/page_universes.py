"""Shared fictional universes — collaborative storytelling."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import streamlit as st

from lib import auth, storage, ui


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def render() -> None:
    ui.section("Shared universes")
    st.caption(
        "Build a fictional world together. Other writers can set their own "
        "stories of different genres in the same universe."
    )

    universes = storage.read_collection("universes")
    user = auth.current_user()

    with st.expander("Create a new shared universe", expanded=not universes):
        if not user:
            st.info("Sign in to create a universe.")
        else:
            name = st.text_input("Universe name")
            tagline = st.text_input("Tagline")
            rules = st.text_area(
                "Canon & collaboration rules",
                placeholder="Setting, timeline, key characters, what contributors can and cannot change...",
                height=140,
            )
            if st.button("Create universe", type="primary", disabled=not name):
                storage.append_document(
                    "universes",
                    {
                        "id": uuid.uuid4().hex,
                        "name": name.strip(),
                        "tagline": tagline.strip(),
                        "rules": rules.strip(),
                        "creator_id": user["id"],
                        "creator_name": user["display_name"],
                        "created_at": _now(),
                    },
                )
                st.success("Universe created. Writers can now add stories to it.")
                st.rerun()

    if not universes:
        st.info("No shared universes yet. Create the first one above!")
        return

    stories = storage.read_collection("stories")
    for uni in sorted(universes, key=lambda u: u.get("created_at", ""), reverse=True):
        related = [
            s for s in stories
            if s.get("universe_name") == uni.get("name") and s.get("status") == "published"
        ]
        st.markdown(
            f"""<div class="ink-card">
            <h4>{uni.get('name')}</h4>
            <p><em>{uni.get('tagline', '')}</em></p>
            <p>Created by <strong>{uni.get('creator_name', 'Unknown')}</strong> ·
            {len(related)} contributing stories</p>
            </div>""",
            unsafe_allow_html=True,
        )
        with st.expander("Canon rules & contributing stories"):
            st.markdown("**Canon & collaboration rules**")
            st.write(uni.get("rules") or "_No rules specified._")
            st.markdown("**Stories in this universe**")
            if related:
                for s in related:
                    badges = "".join(ui.genre_badge(g) for g in s.get("genres", []))
                    st.markdown(
                        f"- **{s.get('title')}** by {s.get('author_name')} {badges}",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No stories yet — add one from Write & publish.")
