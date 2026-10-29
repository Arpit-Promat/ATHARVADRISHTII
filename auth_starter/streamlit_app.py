import os, streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth import register_user, login_user, verify_email_token, reload_session_user, resend_token, rate_allowed
from email_service import send_verification_email

st.set_page_config(page_title="ATHARVADRISHTI Account", page_icon="🌿")
def cfg(name, default=None):
    if os.getenv(name): return os.getenv(name)
    try: return st.secrets.get(name, default)
    except Exception: return default
@st.cache_resource
def factory():
    url = cfg("DATABASE_URL")
    if not url: raise RuntimeError("DATABASE_URL is missing from Streamlit secrets.")
    return sessionmaker(bind=create_engine(url, pool_pre_ping=True, pool_recycle=300), expire_on_commit=False)
try:
    Session = factory()
except Exception as exc:
    st.error(str(exc)); st.stop()

token = st.query_params.get("verify")
if token:
    with Session() as db: ok = verify_email_token(db, token)
    st.query_params.clear()
    st.success("Email verified. You can sign in.") if ok else st.error("Link invalid, expired, or already used.")

if st.session_state.get("user_id"):
    with Session() as db:
        user = reload_session_user(db, st.session_state["user_id"])
        if not user: st.session_state.pop("user_id", None)
        else:
            st.title("Your account"); st.write(user.display_name)
            if not user.email_verified_at:
                st.warning("Your email is not verified.")
                if st.button("Resend verification link"):
                    key = "resend:" + str(user.id)
                    if not rate_allowed(key, 1, 60): st.warning("Please wait before resending.")
                    else: st.info(send_verification_email(user.email, resend_token(db, user))[1])
            if st.button("Sign out"):
                user.cookie_nonce = __import__("secrets").token_urlsafe(24); db.commit()
                st.session_state.pop("user_id", None); st.rerun()
            st.stop()

st.title("ATHARVADRISHTI")
login_tab, register_tab = st.tabs(["Sign in", "Create account"])
with login_tab:
    with st.form("login"):
        email = st.text_input("Email"); password = st.text_input("Password", type="password")
        code = st.text_input("Authenticator code (if enabled)", max_chars=6)
        submitted = st.form_submit_button("Sign in")
    if submitted:
        with Session() as db:
            user, msg = login_user(db, email, password, code or None)
            if user: st.session_state["user_id"] = str(user.id); st.success(msg); st.rerun()
            else: st.error(msg)
with register_tab:
    with st.form("register"):
        name = st.text_input("Full name"); email = st.text_input("Email address", key="reg_email")
        password = st.text_input("Password (12+ characters)", type="password", key="reg_password")
        confirm = st.text_input("Confirm password", type="password")
        age = st.checkbox("I confirm I meet the minimum age requirement.")
        terms = st.checkbox("I accept the Privacy Policy and Terms.")
        submitted = st.form_submit_button("Create account")
    if submitted:
        if password != confirm: st.error("Passwords do not match.")
        else:
            with Session() as db:
                user, raw, msg = register_user(db, email, name, password, age, terms)
                if user:
                    st.success(msg); st.info(send_verification_email(user.email, raw)[1])
                else: st.error(msg)
