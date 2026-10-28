import streamlit as st
from streamlit_native_auth import create_user, issue_otp

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
st.markdown('<p class="muted">Build a secure plant-health workspace with verified contact details.</p>', unsafe_allow_html=True)

with st.form("signup"):
    name = st.text_input("Full name")
    email = st.text_input("Email address")
    phone = st.text_input("Mobile number", placeholder="+919876543210")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm password", type="password")
    submitted = st.form_submit_button("Create account", use_container_width=True, type="primary")

if submitted:
    if password != confirm:
        st.error("Passwords do not match.")
    else:
        user, error = create_user(name, email, phone, password)
        if error:
            st.error(error)
        else:
            st.session_state["verify_email"] = user["email"]
            st.session_state["verify_phone"] = user["phone"]
            delivery_errors = []
            try:
                issue_otp(user["id"], "email_verification", "email", user["email"])
            except Exception as exc:
                delivery_errors.append(f"Email: {exc}")
            if delivery_errors:
                st.session_state["verification_delivery_errors"] = [
                    "Your account was created, but verification delivery needs configuration.",
                    *delivery_errors,
                    "Add the provider credentials in Streamlit Secrets, then use Resend codes on this page.",
                ]
            else:
                st.success("Account created. Verification codes were sent.")
            if st.session_state.get("dev_otp_codes"):
                st.warning("Development-only OTPs (never enable this in production):")
                for purpose, details in st.session_state["dev_otp_codes"].items():
                    st.code(f"{purpose}: {details['code']}")
            st.switch_page("pages/3_Verify.py")

if st.button("Back to home", use_container_width=True):
    st.switch_page("streamlit_app.py")
st.markdown('<div class="hint">🛡️ Verify your email to activate your account. Mobile verification and OTP-based 2FA are optional and require SMS provider configuration.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
