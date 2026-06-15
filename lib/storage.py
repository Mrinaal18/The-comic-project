"""
storage.py
==========
A tiny JSON document store that persists to a GitHub repository so data survives
Streamlit Community Cloud's ephemeral filesystem.

Design
------
* Each "collection" (users, stories, films, etc.) is a single JSON file inside
  the configured data folder of a GitHub repo.
* Reads are cached in Streamlit's session/resource cache for speed.
* Writes commit the updated JSON file back to GitHub via the contents API.
* If no GitHub token is configured, the store transparently falls back to a
  local `local_data/` folder so the app still runs (useful for local dev/demo).

This keeps the whole app dependency-light: no SQL server required, and the data
itself is version-controlled and auditable in GitHub.
"""

from __future__ import annotations

import json
import os
import threading
from typing import Any

import streamlit as st

try:  # PyGithub is optional at import time so local fallback still works.
    from github import Github, GithubException
    from github.InputGitTreeElement import InputGitTreeElement  # noqa: F401
except Exception:  # pragma: no cover
    Github = None
    GithubException = Exception


# A module-level lock to avoid two writes racing within the same process.
_WRITE_LOCK = threading.Lock()

LOCAL_DIR = "local_data"


def _secret(key: str, default: Any = None) -> Any:
    """Read a value from st.secrets, then env vars, then a default."""
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key.upper(), default)


def github_enabled() -> bool:
    """True when a GitHub token + repo are configured and PyGithub is present."""
    return bool(_secret("github_token") and _secret("github_repo") and Github)


# --------------------------------------------------------------------------- #
# GitHub client (cached as a resource for the life of the app process)
# --------------------------------------------------------------------------- #
@st.cache_resource(show_spinner=False)
def _get_repo():
    token = _secret("github_token")
    repo_name = _secret("github_repo")
    gh = Github(token)
    return gh.get_repo(repo_name)


def _data_path(collection: str) -> str:
    folder = _secret("github_data_path", "data")
    return f"{folder.rstrip('/')}/{collection}.json"


def _branch() -> str:
    return _secret("github_branch", "main")


# --------------------------------------------------------------------------- #
# Local fallback helpers
# --------------------------------------------------------------------------- #
def _local_path(collection: str) -> str:
    os.makedirs(LOCAL_DIR, exist_ok=True)
    return os.path.join(LOCAL_DIR, f"{collection}.json")


def _read_local(collection: str) -> list[dict]:
    path = _local_path(collection)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return []


def _write_local(collection: str, rows: list[dict]) -> None:
    with open(_local_path(collection), "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def read_collection(collection: str) -> list[dict]:
    """Return all documents in a collection as a list of dicts."""
    if not github_enabled():
        return _read_local(collection)

    try:
        repo = _get_repo()
        contents = repo.get_contents(_data_path(collection), ref=_branch())
        raw = contents.decoded_content.decode("utf-8")
        return json.loads(raw) if raw.strip() else []
    except GithubException as exc:  # File may not exist yet -> empty collection.
        if getattr(exc, "status", None) == 404:
            return []
        raise
    except Exception:
        # On any unexpected error, degrade gracefully to local cache.
        return _read_local(collection)


def write_collection(collection: str, rows: list[dict]) -> None:
    """Persist the full list of documents for a collection."""
    if not github_enabled():
        _write_local(collection, rows)
        return

    payload = json.dumps(rows, indent=2, ensure_ascii=False)
    path = _data_path(collection)
    branch = _branch()
    message = f"chore(data): update {collection}.json"

    with _WRITE_LOCK:
        repo = _get_repo()
        try:
            existing = repo.get_contents(path, ref=branch)
            repo.update_file(path, message, payload, existing.sha, branch=branch)
        except GithubException as exc:
            if getattr(exc, "status", None) == 404:
                repo.create_file(path, message, payload, branch=branch)
            else:
                raise
        # Keep a local mirror so reads within this session are instant.
        _write_local(collection, rows)


def append_document(collection: str, doc: dict) -> dict:
    """Append a single document and persist. Returns the stored doc."""
    rows = read_collection(collection)
    rows.append(doc)
    write_collection(collection, rows)
    return doc


def update_document(collection: str, doc_id: str, patch: dict) -> dict | None:
    """Patch a document matched by its 'id' field. Returns the updated doc."""
    rows = read_collection(collection)
    updated = None
    for row in rows:
        if row.get("id") == doc_id:
            row.update(patch)
            updated = row
            break
    if updated is not None:
        write_collection(collection, rows)
    return updated


def find_one(collection: str, **filters) -> dict | None:
    """Return the first document matching all key/value filters."""
    for row in read_collection(collection):
        if all(row.get(k) == v for k, v in filters.items()):
            return row
    return None


def find_many(collection: str, **filters) -> list[dict]:
    """Return all documents matching all key/value filters."""
    if not filters:
        return read_collection(collection)
    return [
        row
        for row in read_collection(collection)
        if all(row.get(k) == v for k, v in filters.items())
    ]
