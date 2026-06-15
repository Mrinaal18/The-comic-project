"""Explore / read published stories."""

from __future__ import annotations

import streamlit as st

from lib import storage, ui


def _story_card(story: dict) -> None:
    badges = "".join(ui.genre_badge(g) for g in story.get("genres", []))
    st.markdown(
        f"""<div class="ink-card">
        <h4>{story.get('title', 'Untitled')}</h4>
        <p>by <strong>{story.get('author_name', 'Unknown')}</strong>
        &nbsp;·&nbsp; {story.get('word_count', 0)} words</p>
        <div style="margin:8px 0;">{badges}</div>
        <p>{(story.get('synopsis') or '')[:240]}</p>
        </div>""",
        unsafe_allow_html=True,
    )


def render() -> None:
    ui.section("Explore stories")
    st.caption("Discover original fiction and fan fiction from the community.")

    stories = [s for s in storage.read_collection("stories") if s.get("status") == "published"]

    f1, f2, f3 = st.columns([1.4, 1, 1])
    with f1:
        query = st.text_input("Search by title, author, or synopsis", "")
    with f2:
        genre = st.selectbox("Genre", ["All"] + ui.GENRES)
    with f3:
        sort = st.selectbox("Sort by", ["Newest", "Most words", "Title A-Z"])

    def matches(s: dict) -> bool:
        if genre != "All" and genre not in s.get("genres", []):
            return False
        if query:
            hay = " ".join(
                [s.get("title", ""), s.get("author_name", ""), s.get("synopsis", "")]
            ).lower()
            if query.lower() not in hay:
                return False
        return True

    results = [s for s in stories if matches(s)]
    if sort == "Most words":
        results.sort(key=lambda s: s.get("word_count", 0), reverse=True)
    elif sort == "Title A-Z":
        results.sort(key=lambda s: s.get("title", "").lower())
    else:
        results.sort(key=lambda s: s.get("created_at", ""), reverse=True)

    if not results:
        st.info("No stories yet. Be the first to publish from the Write & publish page!")
        return

    st.write(f"**{len(results)}** stories found.")
    for story in results:
        _story_card(story)
        with st.expander("Read full story"):
            if story.get("universe_name"):
                st.caption(f"Part of the shared universe: {story['universe_name']}")
            st.markdown(story.get("body", "_No content._"))

            films = storage.find_many("films", story_id=story.get("id"))
            if films:
                st.markdown("**Short-film adaptations**")
                for film in films:
                    st.markdown(f"- [{film.get('title')}]({film.get('url')}) — {film.get('director', '')}")
