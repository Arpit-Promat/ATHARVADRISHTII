import os, requests
def cfg(k, default=None):
    if os.getenv(k): return os.getenv(k)
    try:
        import streamlit as st
        return st.secrets.get(k, default)
    except Exception: return default
def send_verification_email(to_email, token):
    key=cfg("RESEND_API_KEY"); base=cfg("APP_BASE_URL","").rstrip("/")
    if not key: return False, "Email service is not configured; account remains unverified."
    if not base.startswith("https://"): return False, "APP_BASE_URL must use HTTPS."
    sender=cfg("EMAIL_FROM","ATHARVADRISHTI <onboarding@resend.dev>")
    try:
        r=requests.post("https://api.resend.com/emails",
            headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
            json={"from":sender,"to":[to_email],"subject":"Verify your ATHARVADRISHTI email",
                  "html":f'<p>This link expires in 24 hours.</p><p><a href="{base}/?verify={token}">Verify email</a></p>'},
            timeout=15)
        return (True,"Verification email sent.") if r.ok else (False,f"Email provider returned HTTP {r.status_code}.")
    except requests.RequestException:
        return False, "Could not connect to email provider. Try again later."
