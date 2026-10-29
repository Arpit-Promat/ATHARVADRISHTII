import streamlit as st
from supabase_auth import sign_up_user

st.set_page_config(page_title="Sign Up | ATHARVADRISHTI", page_icon="🌿", layout="centered")
st.markdown("""
<style>
.stApp{background:#f7faf5}.block-container{max-width:620px;padding-top:3rem}
.auth-card{padding:32px;border:1px solid #dce8dc;border-radius:28px;background:#fff;box-shadow:0 20px 60px rgba(20,80,40,.10)}
.auth-title{font:700 34px Arial,sans-serif;color:#10251a}.muted{color:#6b7e71}.hint{padding:12px 14px;border-radius:12px;background:#eef8ef;color:#2c7443;font-size:12px}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="auth-card">', unsafe_allow_html=True)
st.markdown("## 🌿 ATHARVADRISHTI")
st.markdown('<div class="auth-title">Create your account</div>', unsafe_allow_html=True)
st.markdown('<p class="muted">Create your personal plant-health workspace.</p>', unsafe_allow_html=True)

with st.form("signup"):
    name = st.text_input("Full name")
    email = st.text_input("Email address")
    phone = st.text_input("Mobile number (optional)", placeholder="+919876543210")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm password", type="password")
    submitted = st.form_submit_button("Create account", use_container_width=True, type="primary")

if submitted:
    if password != confirm:
        st.error("Passwords do not match.")
    else:
        user, error = sign_up_user(name, email, phone, password)
        if error:
            st.error(error)
        elif user:
            st.success("Account created successfully.")
            st.switch_page("pages/1_AI_Scanner.py")

if st.button("Back to home", use_container_width=True):
    st.switch_page("streamlit_app.py")
st.markdown('<div class="hint">🛡️ Authentication is handled by Supabase. Email confirmation is temporarily disabled for this setup; enable it before a public production launch.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
