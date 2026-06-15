"""Short-film adaptations — upload (link) & showcase."""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

import streamlit as st

from lib import auth, storage, ui


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_video_url(url: str) -> bool:
    return bool(re.match(r"https?://", url or ""))


def render() -> None:
    ui.section("Short films")
    st.caption(
        "Showcase short-film adaptations of community stories. Paste a YouTube or "
        "Vimeo link and connect it to the original work."
    )

    user = auth.current_user()
    stories = [s for s in storage.read_collection("stories") if s.get("status") == "published"]
    story_map = {f"{s.get('title')} — {s.get('author_name')}": s.get("id") for s in stories}

    with st.expander("Add a short film", expanded=False):
        if not user:
            st.info("Sign in to add a film.")
        elif not stories:
            st.info("Publish a story first — films are linked to a published work.")
        else:
            f_title = st.text_input("Film title")
            f_story = st.selectbox("Based on which story?", list(story_map.keys()))
            f_director = st.text_input("Director / creator")
            f_url = st.text_input("Video link (YouTube, Vimeo, etc.)")
            f_desc = st.text_area("Description", height=80)
            valid = f_title and _is_video_url(f_url)
            if not f_url == "" and not _is_video_url(f_url):
                st.warning("Please enter a valid http(s) video URL.")
            if st.button("Add film", type="primary", disabled=not valid):
                storage.append_document(
                    "films",
                    {
                        "id": uuid.uuid4().hex,
                        "title": f_title.strip(),
                        "story_id": story_map[f_story],
                        "story_title": f_story.split(" — ")[0],
                        "director": f_director.strip(),
                        "url": f_url.strip(),
                        "description": f_desc.strip(),
                        "uploader_id": user["id"],
                        "uploader_name": user["display_name"],
                        "created_at": _now(),
                    },
                )
                st.success("Film added to the showcase.")
                st.rerun()

    films = storage.read_collection("films")
    if not films:
        st.info("No short films yet. Add the first adaptation above!")
        return

    st.write(f"**{len(films)}** short films in the showcase.")
    cols = st.columns(2)
    for i, film in enumerate(sorted(films, key=lambda f: f.get("created_at", ""), reverse=True)):
        with cols[i % 2]:
            st.markdown(
                f"""<div class="ink-card">
                <h4>{film.get('title')}</h4>
                <p>Adapted from <strong>{film.get('story_title', '')}</strong></p>
                <p>Directed by {film.get('director') or 'Unknown'} ·
                added by {film.get('uploader_name', '')}</p>
                <p>{film.get('description', '')}</p>
                </div>""",
                unsafe_allow_html=True,
            )
            try:
                st.video(film.get("url"))
            except Exception:
                st.markdown(f"[Watch the film]({film.get('url')})")
