"""
copyright_checker.py
====================
AI-powered originality / copyright-infringement checker (Problem 2).

Two complementary signals are combined:

1. Embedding similarity
   The draft is embedded and compared (cosine similarity) against a reference
   database of known works' plot summaries. High similarity flags potential
   overlap fast and cheaply.

2. LLM plot-point analysis
   For the top matches, an LLM is asked to compare specific plot points,
   characters and structure, and to report any concrete overlaps along with a
   risk level and guidance. This catches paraphrased/structural similarity that
   raw text matching misses.

The reference database is stored in the GitHub JSON store under the
"reference_works" collection and seeded from data/seed_reference_works.json on
first run. Writers' own published stories are ALSO checked, so the platform
protects everyone's intellectual property — including its own community.

Requires `openai_api_key` in secrets. Without it, the module returns a clear
"AI disabled" result instead of crashing.
"""

from __future__ import annotations

import json
import math
import os

import streamlit as st

from lib import storage

REFERENCE = "reference_works"


def _secret(key, default=None):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key.upper(), default)


def ai_enabled() -> bool:
    return bool(_secret("openai_api_key"))


@st.cache_resource(show_spinner=False)
def _client():
    from openai import OpenAI

    return OpenAI(api_key=_secret("openai_api_key"))


# --------------------------------------------------------------------------- #
# Reference database
# --------------------------------------------------------------------------- #
def _seed_reference_if_empty() -> None:
    if storage.read_collection(REFERENCE):
        return
    seed_path = os.path.join("data", "seed_reference_works.json")
    if os.path.exists(seed_path):
        try:
            with open(seed_path, "r", encoding="utf-8") as fh:
                seed = json.load(fh)
            storage.write_collection(REFERENCE, seed)
        except Exception:
            pass


def reference_works() -> list[dict]:
    _seed_reference_if_empty()
    works = list(storage.read_collection(REFERENCE))
    # Also compare against community-published stories.
    for story in storage.find_many("stories", status="published"):
        works.append(
            {
                "id": f"story:{story.get('id')}",
                "title": story.get("title", "Untitled"),
                "author": story.get("author_name", "Community author"),
                "summary": (story.get("synopsis") or story.get("body", ""))[:1500],
                "source": "Inkverse community",
            }
        )
    return works


# --------------------------------------------------------------------------- #
# Embedding similarity
# --------------------------------------------------------------------------- #
def _embed(texts: list[str]) -> list[list[float]]:
    model = _secret("openai_embedding_model", "text-embedding-3-small")
    resp = _client().embeddings.create(model=model, input=texts)
    return [d.embedding for d in resp.data]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


# --------------------------------------------------------------------------- #
# LLM plot-point comparison
# --------------------------------------------------------------------------- #
_ANALYSIS_SYSTEM = (
    "You are a literary copyright analyst. You compare a NEW draft against an "
    "EXISTING published work and identify concrete overlaps in plot points, "
    "character archetypes, settings, structure, and distinctive phrasing. "
    "Generic tropes (e.g. 'a hero's journey', 'enemies to lovers') are NOT "
    "infringement and must be called common tropes, not overlaps. Respond "
    "ONLY with strict JSON matching the requested schema."
)


def _analyze_pair(draft: str, work: dict) -> dict:
    model = _secret("openai_chat_model", "gpt-4o-mini")
    prompt = f"""
Compare the NEW DRAFT against the EXISTING WORK.

EXISTING WORK
Title: {work.get('title')}
Author: {work.get('author')}
Summary: {work.get('summary')}

NEW DRAFT
{draft[:6000]}

Return JSON with this exact schema:
{{
  "risk_level": "none" | "low" | "medium" | "high",
  "similarity_explanation": "1-3 sentence summary",
  "overlaps": ["specific concrete overlap", "..."],
  "common_tropes": ["shared but non-infringing trope", "..."],
  "recommendation": "actionable guidance for the writer"
}}
""".strip()

    resp = _client().chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _ANALYSIS_SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )
    try:
        return json.loads(resp.choices[0].message.content)
    except Exception:
        return {
            "risk_level": "low",
            "similarity_explanation": "Could not parse AI response.",
            "overlaps": [],
            "common_tropes": [],
            "recommendation": "Please re-run the check.",
        }


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #
def check_draft(draft: str, top_k: int = 3, threshold: float = 0.30) -> dict:
    """
    Run the full originality check on a draft.

    Returns a dict:
    {
      "ai_enabled": bool,
      "message": str | None,
      "candidates": [ {work fields..., "similarity": float, "analysis": {...}} ],
      "overall_risk": "none|low|medium|high",
    }
    """
    if not draft or len(draft.strip()) < 40:
        return {
            "ai_enabled": ai_enabled(),
            "message": "Please paste at least a few sentences of your draft.",
            "candidates": [],
            "overall_risk": "none",
        }

    if not ai_enabled():
        return {
            "ai_enabled": False,
            "message": (
                "AI checking is disabled. Add `openai_api_key` to your Streamlit "
                "secrets to enable embedding similarity and plot-point analysis."
            ),
            "candidates": [],
            "overall_risk": "none",
        }

    works = reference_works()
    if not works:
        return {
            "ai_enabled": True,
            "message": "No reference works available to compare against yet.",
            "candidates": [],
            "overall_risk": "none",
        }

    # 1) Embedding similarity to rank candidates.
    summaries = [w.get("summary", "") for w in works]
    vectors = _embed([draft[:6000]] + summaries)
    draft_vec, work_vecs = vectors[0], vectors[1:]

    scored = []
    for work, vec in zip(works, work_vecs):
        scored.append((_cosine(draft_vec, vec), work))
    scored.sort(key=lambda t: t[0], reverse=True)

    # 2) LLM analysis for top candidates above threshold.
    candidates = []
    risk_rank = {"none": 0, "low": 1, "medium": 2, "high": 3}
    overall = "none"
    for similarity, work in scored[:top_k]:
        if similarity < threshold:
            continue
        analysis = _analyze_pair(draft, work)
        candidates.append({**work, "similarity": round(similarity, 3), "analysis": analysis})
        lvl = analysis.get("risk_level", "low")
        if risk_rank.get(lvl, 0) > risk_rank.get(overall, 0):
            overall = lvl

    message = None
    if not candidates:
        message = "No significant overlaps detected against the reference database."

    return {
        "ai_enabled": True,
        "message": message,
        "candidates": candidates,
        "overall_risk": overall,
    }
