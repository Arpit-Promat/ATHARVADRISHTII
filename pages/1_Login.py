import streamlit as st
from app_supabase_auth import authenticate

st.set_page_config(page_title="Login | ATHARVADRISHTI", page_icon="ðŸŒ¿", layout="centered")
st.markdown("""
<style>
.stApp{background:#f7faf5}.block-container{max-width:620px;padding-top:3rem}
.auth-card{padding:30px;border:1px solid #dce8dc;border-radius:24px;background:#fff;box-shadow:0 20px 60px rgba(20,80,40,.10)}
.auth-title{font:700 34px Arial,sans-serif;color:#10251a}.muted{color:#6b7e71}.security{padding:12px 14px;border-radius:12px;background:#eef8ef;color:#2c7443;font-size:12px}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="auth-card">', unsafe_allow_html=True)
st.markdown("## ðŸŒ¿ ATHARVADRISHTI")
st.markdown('<div class="auth-title">Welcome Back</div>', unsafe_allow_html=True)
st.markdown('<p class="muted">Login with your email address.</p>', unsafe_allow_html=True)

email = st.text_input("Email Address", key="login_identity")
password = st.text_input("Password", type="password", key="login_password")

if st.button("Login", use_container_width=True, type="primary"):
    user, error = authenticate(email, password)
    if error:
        st.error(error)
    elif user:
        st.success("Login successful.")
        st.switch_page("pages/1_AI_Scanner.py")

c1, c2 = st.columns(2)
with c1:
    if st.button("Create account", use_container_width=True):
        st.switch_page("pages/2_Sign_Up.py")
with c2:
    if st.button("Back to Home", use_container_width=True):
        st.switch_page("streamlit_app.py")

st.markdown('<div class="security">ðŸ›¡ï¸ Secure Supabase email/password authentication Â· Private scan history</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

