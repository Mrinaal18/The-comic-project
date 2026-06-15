"""Standalone AI copyright / originality checker (Problem 2)."""

from __future__ import annotations

import streamlit as st

from lib import storage, ui
from lib.copyright_checker import check_draft, ai_enabled, reference_works


def render() -> None:
    ui.section("Copyright & originality check")
    st.caption(
        "Paste a draft to scan it against a database of known works and community "
        "stories. The AI flags overlapping plot points, characters, and structure "
        "so you can avoid accidental infringement before you publish."
    )

    if not ai_enabled():
        st.warning(
            "AI checking is currently disabled. Add `openai_api_key` to your "
            "Streamlit secrets to enable embedding similarity and plot-point analysis."
        )

    draft = st.text_area(
        "Your draft or synopsis",
        height=280,
        placeholder="Paste the text you want to check...",
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        top_k = st.slider("How many top matches to analyze", 1, 5, 3)
    with c2:
        threshold = st.slider("Similarity sensitivity", 0.10, 0.60, 0.30, 0.05)

    if st.button("Run originality check", type="primary", disabled=not draft):
        with st.spinner("Analyzing your draft..."):
            result = check_draft(draft, top_k=top_k, threshold=threshold)

        if result.get("message"):
            st.info(result["message"])

        st.markdown(
            "### Overall risk: " + ui.risk_chip(result.get("overall_risk", "none")),
            unsafe_allow_html=True,
        )

        for cand in result.get("candidates", []):
            analysis = cand.get("analysis", {})
            st.markdown(
                f"""<div class="ink-card">
                <h4>{cand.get('title')} <span style="font-size:0.8rem;color:#6B7280;">
                by {cand.get('author')}</span></h4>
                <p>Embedding similarity: <strong>{cand.get('similarity')}</strong> ·
                Source: {cand.get('source', 'reference')}</p>
                </div>""",
                unsafe_allow_html=True,
            )
            st.markdown(ui.risk_chip(analysis.get("risk_level", "low")), unsafe_allow_html=True)
            st.write(analysis.get("similarity_explanation", ""))
            if analysis.get("overlaps"):
                st.markdown("**Potential overlaps to review**")
                for o in analysis["overlaps"]:
                    st.markdown(f"- {o}")
            if analysis.get("common_tropes"):
                st.markdown("**Common tropes (not infringement)**")
                for t in analysis["common_tropes"]:
                    st.markdown(f"- {t}")
            if analysis.get("recommendation"):
                st.success(analysis["recommendation"])
            st.divider()

        st.caption(
            "This tool offers automated guidance and is not legal advice. For "
            "high-risk findings, consult a qualified IP attorney."
        )

    with st.expander("What's in the reference database?"):
        works = reference_works()
        st.write(f"Comparing against **{len(works)}** works (public-domain seeds + community stories).")
        for w in works:
            st.markdown(f"- **{w.get('title')}** — {w.get('author')} ({w.get('source', '')})")
