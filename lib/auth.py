"""
auth.py
=======
Simple username/password authentication backed by the GitHub JSON store.

* Passwords are hashed with bcrypt (never stored in plaintext).
* The signed-in user is kept in st.session_state.
* Each writer "owns" the works/films they create (matched by user id).

This is intentionally lightweight — appropriate for a community storytelling
platform/prototype — while still following the important security basics
(salted hashing, no plaintext, server-side checks).
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

import bcrypt
import streamlit as st

from lib import storage

USERS = "users"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def valid_username(username: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_]{3,24}", username or ""))


def signup(username: str, password: str, display_name: str, bio: str = "") -> tuple[bool, str]:
    """Create a new account. Returns (success, message)."""
    username = (username or "").strip().lower()
    display_name = (display_name or "").strip() or username

    if not valid_username(username):
        return False, "Username must be 3-24 chars: letters, numbers, underscores."
    if len(password or "") < 6:
        return False, "Password must be at least 6 characters."
    if storage.find_one(USERS, username=username):
        return False, "That username is already taken."

    user = {
        "id": uuid.uuid4().hex,
        "username": username,
        "display_name": display_name,
        "bio": bio.strip(),
        "password_hash": _hash_password(password),
        "created_at": _now(),
    }
    storage.append_document(USERS, user)
    return True, "Account created. You can now sign in."


def login(username: str, password: str) -> tuple[bool, str]:
    """Authenticate and set the session. Returns (success, message)."""
    username = (username or "").strip().lower()
    user = storage.find_one(USERS, username=username)
    if not user or not _verify_password(password, user.get("password_hash", "")):
        return False, "Invalid username or password."

    st.session_state["user"] = {
        "id": user["id"],
        "username": user["username"],
        "display_name": user.get("display_name", user["username"]),
        "bio": user.get("bio", ""),
    }
    return True, f"Welcome back, {user.get('display_name', username)}!"


def logout() -> None:
    st.session_state.pop("user", None)


def current_user() -> dict | None:
    return st.session_state.get("user")


def require_login() -> dict | None:
    """Return the current user, or None. UI decides what to show."""
    return current_user()
