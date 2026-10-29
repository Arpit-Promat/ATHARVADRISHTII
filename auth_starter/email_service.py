import os
import requests

def cfg(name, default=None):
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st
        return st.secrets.get(name, default)
    except Exception:
        return default

def send_verification_email(to_email: str, token: str) -> tuple[bool, str]:
    api_key = cfg("RESEND_API_KEY")
    base_url = (cfg("APP_BASE_URL", "") or "").rstrip("/")
    if not api_key:
        return False, "Email is not configured; the account remains unverified."
    if not base_url.startswith("https://"):
        return False, "APP_BASE_URL must be an HTTPS URL."
    sender = cfg("EMAIL_FROM", "ATHARVADRISHTI <onboarding@resend.dev>")
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"from": sender, "to": [to_email], "subject": "Verify your ATHARVADRISHTI email",
                  "html": f'<p>This link expires in 24 hours.</p><p><a href="{base_url}/?verify={token}">Verify email</a></p>'},
            timeout=15,
        )
        if response.ok:
            return True, "Verification email sent."
        return False, f"Email provider returned HTTP {response.status_code}."
    except requests.RequestException:
        return False, "Could not connect to the email provider. Try again later."
