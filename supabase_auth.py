"""Supabase Auth integration for the ATHARVADRISHTI Streamlit app.

Configure SUPABASE_URL and SUPABASE_ANON_KEY in .streamlit/secrets.toml.
The key value may be a Supabase publishable key (sb_publishable_...) or legacy anon key.
Never use a service_role or sb_secret key in this app.
"""
from __future__ import annotations

import os
from typing import Any

import streamlit as st
from supabase import Client, create_client


def _secret(name: str) -> str:
    try:
        value = st.secrets.get(name, "")
    except Exception:
        value = ""
    return str(value or os.getenv(name, "") or "").strip()


def _new_client() -> Client:
    url = _secret("SUPABASE_URL")
    key = _secret("SUPABASE_ANON_KEY")
    if not url or not key:
        raise RuntimeError(
            "Supabase is not configured. Add SUPABASE_URL and "
            "SUPABASE_ANON_KEY to .streamlit/secrets.toml."
        )
    return create_client(url, key)


def _user_dict(raw_user: Any) -> dict[str, Any] | None:
    if raw_user is None:
        return None
    metadata = getattr(raw_user, "user_metadata", None) or {}
    return {
        "id": str(getattr(raw_user, "id", "")),
        "email": str(getattr(raw_user, "email", "") or ""),
        "name": str(metadata.get("full_name") or metadata.get("name") or "User"),
        "phone": str(metadata.get("phone") or ""),
    }


def _remember_session(session: Any) -> None:
    if session is None:
        return
    st.session_state["supabase_access_token"] = session.access_token
    st.session_state["supabase_refresh_token"] = session.refresh_token


def sign_up_user(name: str, email: str, phone: str, password: str) -> tuple[dict[str, Any] | None, str | None]:
    name = str(name or "").strip()
    email = str(email or "").strip().lower()
    phone = str(phone or "").strip()
    password = str(password or "")
    if not name:
        return None, "Please enter your name."
    if "@" not in email or len(email) > 255:
        return None, "Please enter a valid email address."
    if len(password) < 8:
        return None, "Password must be at least 8 characters."

    try:
        client = _new_client()
        response = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"full_name": name, "phone": phone}},
        })
        user = _user_dict(response.user)
        if response.session is None:
            return user, (
                "Account created, but Supabase did not start a session. "
                "For the temporary no-verification setup, turn off Confirm Email "
                "in Supabase Authentication settings, then try again."
            )
        _remember_session(response.session)
        if user:
            session_login(user)
        return user, None
    except Exception as exc:
        return None, f"Could not create account: {exc}"


def authenticate(identity: str, password: str) -> tuple[dict[str, Any] | None, str | None]:
    email = str(identity or "").strip().lower()
    if "@" not in email:
        return None, "Please log in using your email address."
    if not password:
        return None, "Please enter your password."
    try:
        response = _new_client().auth.sign_in_with_password({
            "email": email,
            "password": str(password),
        })
        user = _user_dict(response.user)
        if response.session is None or user is None:
            return None, "Login did not return an active session. Please try again."
        _remember_session(response.session)
        session_login(user)
        return user, None
    except RuntimeError as exc:
        return None, str(exc)
    except Exception:
        return None, "Login failed. Check your email and password, then try again."


def session_login(user: dict[str, Any]) -> None:
    st.session_state["authenticated"] = True
    st.session_state["auth_user_id"] = str(user["id"])
    st.session_state["auth_user"] = user


def get_authenticated_client() -> Client:
    client = _new_client()
    access_token = st.session_state.get("supabase_access_token")
    refresh_token = st.session_state.get("supabase_refresh_token")
    if not access_token or not refresh_token:
        raise RuntimeError("Your login session has expired. Please log in again.")
    try:
        client.auth.set_session(access_token, refresh_token)
    except Exception as exc:
        session_logout()
        raise RuntimeError("Your login session has expired. Please log in again.") from exc
    return client


def session_logout() -> None:
    try:
        access_token = st.session_state.get("supabase_access_token")
        refresh_token = st.session_state.get("supabase_refresh_token")
        if access_token and refresh_token:
            client = _new_client()
            client.auth.set_session(access_token, refresh_token)
            client.auth.sign_out()
    except Exception:
        # Local logout must still work if the network is unavailable.
        pass
    for key in (
        "authenticated", "auth_user_id", "auth_user",
        "supabase_access_token", "supabase_refresh_token",
        "last_history_scan_key",
    ):
        st.session_state.pop(key, None)


def is_authenticated() -> bool:
    return bool(
        st.session_state.get("authenticated")
        and st.session_state.get("auth_user_id")
        and st.session_state.get("supabase_access_token")
    )


def current_user() -> dict[str, Any] | None:
    if not is_authenticated():
        return None
    return st.session_state.get("auth_user")
