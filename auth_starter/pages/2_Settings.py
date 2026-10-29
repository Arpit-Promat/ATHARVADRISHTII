import io,streamlit as st,qrcode,os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth import setup_totp,enable_totp,disable_totp
from models import User
def cfg(k):
    if os.getenv(k): return os.getenv(k)
    try: return st.secrets.get(k)
    except Exception: return None
@st.cache_resource
def factory(): return sessionmaker(bind=create_engine(cfg("DATABASE_URL"),pool_pre_ping=True),expire_on_commit=False)
if not st.session_state.get("user_id"): st.warning("Sign in first."); st.stop()
with factory()() as db:
    user=db.get(User,st.session_state.user_id)
    if not user or user.deleted_at: st.error("Please sign in again."); st.stop()
    st.title("Security settings")
    if not user.totp_enabled:
        if st.button("Set up authenticator app"):
            secret,uri=setup_totp(user); st.session_state["pending_totp_secret"]=secret; st.session_state["pending_totp_uri"]=uri
        if st.session_state.get("pending_totp_secret"):
            secret=st.session_state["pending_totp_secret"]; img=qrcode.make(st.session_state["pending_totp_uri"])
            buf=io.BytesIO(); img.save(buf,format="PNG"); st.image(buf.getvalue()); st.code(secret)
            code=st.text_input("Enter authenticator code")
            if st.button("Enable 2FA"):
                if enable_totp(db,user,secret,code):
                    st.session_state.pop("pending_totp_secret",None); st.session_state.pop("pending_totp_uri",None); st.success("2FA enabled."); st.rerun()
                else: st.error("Invalid code.")
    else:
        st.success("2FA enabled."); code=st.text_input("Current code to disable 2FA")
        if st.button("Disable 2FA"):
            ok,msg=disable_totp(db,user,code); st.success(msg) if ok else st.error(msg)
