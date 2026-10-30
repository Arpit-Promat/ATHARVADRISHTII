import streamlit as st
from app_supabase_auth import authenticate, current_user, is_authenticated, session_login, session_logout

st.set_page_config(
    page_title="ATHARVADRISHTI — An Intelligent and Explainable Plant Health Analysis System",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "landing_theme" not in st.session_state:
    st.session_state["landing_theme"] = "light"

is_dark = st.session_state["landing_theme"] == "dark"

if is_dark:
    bg, surface, surface2, text, muted, green, green2, line, soft = (
        "#07120c", "#0d1d13", "#13291a", "#f2faef", "#b8cabc", "#78d49a", "#b2ec86", "#284b35", "#183822"
    )
    button, button_text = "#a7e77e", "#07120c"
else:
    bg, surface, surface2, text, muted, green, green2, line, soft = (
        "#f7faf5", "#ffffff", "#eef5e9", "#10251a", "#63756a", "#1d7b46", "#2fa564", "#d8e6d9", "#edf6e8"
    )
    button, button_text = "#123a24", "#f2faed"

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root{{--bg:{bg};--surface:{surface};--surface2:{surface2};--text:{text};--muted:{muted};--green:{green};--green2:{green2};--line:{line};--soft:{soft};--button:{button};--button-text:{button_text}}}

html, body, .stApp, [data-testid="stAppViewContainer"] {{
    background:var(--bg) !important;
    color:var(--text) !important;
    font-family:'DM Sans',system-ui,sans-serif !important;
}}

.block-container {{
    max-width:1280px !important;
    padding-top:5.0rem !important;
    padding-left:2rem !important;
    padding-right:2rem !important;
    padding-bottom:0 !important;
}}

/* High-contrast Streamlit native controls */
div[data-testid="stButton"] > button {{
    min-height:42px !important;
    border-radius:12px !important;
    border:1px solid var(--line) !important;
    background:var(--surface) !important;
    color:var(--text) !important;
    font-weight:700 !important;
    font-size:13px !important;
    box-shadow:0 5px 16px rgba(18,60,35,.06) !important;
}}

div[data-testid="stButton"] > button:hover {{
    border-color:var(--green2) !important;
    color:var(--green) !important;
    transform:translateY(-1px);
}}

div[data-testid="stButton"] > button[kind="primary"] {{
    background:var(--button) !important;
    color:var(--button-text) !important;
    border-color:var(--button) !important;
}}

div[data-testid="stButton"] > button[kind="primary"]:hover {{
    background:var(--green2) !important;
    color:#fff !important;
}}
.nav-link {{
    display:flex;align-items:center;justify-content:center;min-height:42px;width:100%;
    padding:8px 10px;border:1px solid var(--line);border-radius:12px;
    background:var(--surface);color:var(--text) !important;text-decoration:none !important;
    font-size:13px;font-weight:700;box-shadow:0 5px 16px rgba(18,60,35,.06);
    text-align:center;transition:transform .15s ease,border-color .15s ease;
}}
.nav-link:hover {{border-color:var(--green2);color:var(--green) !important;transform:translateY(-1px)}}
.nav-link.primary {{background:var(--button);color:var(--button-text) !important;border-color:var(--button)}}

div[data-testid="stTextInput"] input {{
    background:var(--surface) !important;
    color:var(--text) !important;
    border:1px solid var(--line) !important;
    border-radius:12px !important;
}}

div[data-testid="stTextInput"] input::placeholder {{color:var(--muted) !important}}

div[data-testid="stTextInput"] label {{color:var(--muted) !important}}

.header-shell {{
    background:var(--surface);
    border:1px solid var(--line);
    border-radius:18px;
    padding:12px 14px;
    box-shadow:0 10px 30px rgba(20,75,38,.08);
}}
.brand-wrap {{display:flex;align-items:center;gap:11px;min-height:43px}}
.brand-mark {{width:43px;height:43px;border-radius:13px;display:grid;place-items:center;background:#10251a;color:#dff7ad;font-size:22px}}
.brand-title {{color:var(--text);font:700 16px/1 'Space Grotesk',sans-serif;letter-spacing:.11em}}
.brand-sub {{margin-top:5px;color:var(--muted);font-size:9px;font-weight:700;letter-spacing:.16em}}

.hero-copy {{padding:50px 0 55px}}
.eyebrow {{display:inline-flex;align-items:center;padding:8px 13px;border-radius:999px;background:var(--soft);color:var(--green);font-size:11px;font-weight:800;letter-spacing:.08em}}
.hero-title {{margin:19px 0 20px;color:var(--text);font:700 clamp(50px,6vw,84px)/.94 'Space Grotesk',sans-serif;letter-spacing:-.06em}}
.hero-title span {{color:var(--green2)}}
.hero-text {{max-width:650px;color:var(--muted);font-size:17px;line-height:1.8}}
.mini-feature {{display:flex;align-items:flex-start;gap:10px;color:var(--text);font-size:12px;font-weight:700;line-height:1.4}}
.mini-feature b {{color:var(--green2);font-size:22px;line-height:1}}

.hero-art {{
    min-height:492px;
    margin-top:45px;
    border-radius:37px;
    background:linear-gradient(145deg,#173b27 0%,#285f3f 50%,#74af62 100%);
    display:grid;place-items:center;position:relative;overflow:hidden;
    box-shadow:0 28px 70px rgba(20,80,40,.20)
}}
.hero-art:before {{content:'';position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.07) 1px,transparent 1px);background-size:32px 32px}}
.phone {{position:relative;z-index:2;width:252px;height:448px;padding:8px;border:7px solid #0f1611;border-radius:40px;background:#d7ead1;box-shadow:0 30px 60px rgba(0,0,0,.24)}}
.phone-screen {{width:100%;height:100%;border-radius:31px;display:grid;place-items:center;position:relative;background:linear-gradient(150deg,#87b466,#dceabd);font-size:114px}}
.scan-box {{position:absolute;inset:62px 27px;border:2px solid rgba(255,255,255,.95);border-radius:22px}}
.disease-chip {{position:absolute;left:17px;right:17px;bottom:18px;padding:12px 13px;background:rgba(255,255,255,.95);color:#285538;border-radius:15px;font-size:11px;font-weight:800;box-shadow:0 8px 22px rgba(0,0,0,.13)}}
.floating {{position:absolute;z-index:3;padding:11px 14px;border:1px solid rgba(255,255,255,.4);border-radius:13px;background:rgba(255,255,255,.95);color:#2a5439;font-size:10px;font-weight:800;box-shadow:0 15px 30px rgba(0,0,0,.18)}}
.floating.a {{top:55px;right:22px}} .floating.b {{left:22px;bottom:72px}}

.login-shell {{margin-top:30px;padding:27px;background:var(--surface);border:1px solid var(--line);border-radius:23px;box-shadow:0 22px 55px rgba(20,80,40,.10)}}
.login-title {{margin-bottom:4px;color:var(--text);font:700 29px 'Space Grotesk',sans-serif}}
.login-sub {{color:var(--muted);font-size:12px;margin-bottom:17px}}
.security-note {{margin-top:13px;padding:10px 12px;border-radius:12px;background:var(--soft);color:var(--green);font-size:10px;font-weight:800}}

.feature-strip {{margin-top:36px;padding:35px 18px;background:var(--surface2);border-top:1px solid var(--line);border-bottom:1px solid var(--line);border-radius:18px}}
.feature-card {{min-height:145px;padding:4px 16px;border-right:1px solid var(--line)}}
.feature-card:last-child {{border-right:0}}
.feature-icon {{font-size:23px}}
.feature-card h3 {{color:var(--text);font-size:14px;margin:8px 0 4px}}
.feature-card p {{color:var(--muted);font-size:10px;line-height:1.55}}

.security-section {{padding:85px 0 70px}}
.security-section h2 {{color:var(--text);font:700 46px 'Space Grotesk',sans-serif;letter-spacing:-.05em;margin:10px 0}}
.security-section>p {{max-width:760px;color:var(--muted);line-height:1.75}}
.step {{min-height:165px;padding:20px;border:1px solid var(--line);border-radius:18px;background:var(--surface);box-shadow:0 9px 24px rgba(20,80,40,.05)}}
.step strong {{color:var(--text);font-size:13px}}
.step p {{color:var(--muted);font-size:10px;line-height:1.55}}
.mini {{margin-top:12px;padding:9px 11px;background:var(--soft);border-radius:10px;color:var(--green);font-size:10px;font-weight:800}}
.green-band {{margin:0 -2rem;padding:38px 2rem;background:#123a24;color:#edf7e9;text-align:center}}
.green-band h2 {{margin:0 0 4px;font:700 29px 'Space Grotesk',sans-serif}}
.green-band p {{margin:0;color:#bdd4c2;font-size:11px}}
.footer {{text-align:center;padding:18px 0 8px;color:var(--muted);font-size:9px}}

/* Responsive foundations */
*, *::before, *::after {{box-sizing:border-box}}
img, svg, video {{max-width:100%;height:auto}}
.block-container {{width:100%;overflow-x:clip}}
[data-testid="stMarkdownContainer"] {{overflow-wrap:anywhere}}
.hero-title {{font-size:clamp(2.65rem, 6vw, 5.25rem);line-height:.98;overflow-wrap:normal}}
.hero-text {{font-size:clamp(1rem, 1.35vw, 1.08rem)}}
.hero-art {{min-height:clamp(340px, 38vw, 492px);width:100%}}
.phone {{width:clamp(190px, 20vw, 252px);height:clamp(340px, 36vw, 448px);max-width:78%}}
.phone-screen {{font-size:clamp(5rem, 8vw, 7.1rem)}}
.disease-chip {{font-size:clamp(9px, .8vw, 11px)}}
.floating {{max-width:42%;white-space:normal;text-align:center}}
.feature-card {{height:100%;min-width:0;overflow-wrap:anywhere}}
.feature-card h3 {{overflow-wrap:anywhere}}
.login-shell {{width:100%;min-width:0}}
input, button {{max-width:100%}}

@media(max-width:1100px){{
    .block-container{{padding-left:1.5rem !important;padding-right:1.5rem !important}}
    .brand-sub{{letter-spacing:.08em;font-size:8px}}
    .brand-title{{font-size:15px;letter-spacing:.08em}}
    .hero-copy{{padding:35px 0 30px}}
    .hero-art{{margin-top:20px;border-radius:30px}}
    .feature-strip{{padding:25px 12px}}
    .security-section{{padding:60px 0 50px}}
    .security-section h2{{font-size:clamp(2rem,4.4vw,2.9rem)}}
}}
@media(max-width:900px){{
    .block-container{{padding-top:4rem !important}}
    .hero-copy{{padding-top:28px}}
    .hero-art{{min-height:390px;margin-top:8px}}
    .feature-card{{border-right:0;border-bottom:1px solid var(--line);padding:15px 8px}}
    .feature-card:last-child{{border-bottom:0}}
    .feature-card h3{{font-size:14px}}
    .feature-card p{{font-size:12px}}
    .step{{min-height:140px}}
    .green-band{{margin-left:-1.5rem;margin-right:-1.5rem;padding-left:1.5rem;padding-right:1.5rem}}
}}
@media(max-width:700px){{
    .block-container{{padding-left:1rem !important;padding-right:1rem !important;padding-top:3.25rem !important}}
    .header-shell{{padding:10px;border-radius:15px}}
    .brand-wrap{{gap:8px;align-items:center}}
    .brand-mark{{width:38px;height:38px;flex:0 0 38px;font-size:20px}}
    .brand-title{{font-size:14px;letter-spacing:.07em}}
    .brand-sub{{font-size:7px;line-height:1.45;letter-spacing:.05em;max-width:250px}}
    [data-testid="stHorizontalBlock"]:has(.nav-row-anchor){{display:flex !important;flex-wrap:wrap !important;gap:8px !important}}
    [data-testid="stHorizontalBlock"]:has(.nav-row-anchor) > [data-testid="column"]{{flex:1 1 calc(33.333% - 8px) !important;min-width:0 !important;width:auto !important}}
    [data-testid="stHorizontalBlock"]:has(.nav-row-anchor) > [data-testid="column"]:first-child{{flex:1 1 100% !important}}
    [data-testid="stHorizontalBlock"]:has(.nav-row-anchor) button{{min-height:42px !important;font-size:12px !important;padding:0 6px !important;white-space:normal !important}}
    .hero-copy{{padding:28px 0 20px}}
    .eyebrow{{font-size:9px;line-height:1.5;white-space:normal}}
    .hero-title{{font-size:clamp(2.55rem, 10.5vw, 4rem);letter-spacing:-.055em;line-height:.98;margin:16px 0}}
    .hero-text{{font-size:15px;line-height:1.7}}
    .mini-feature{{font-size:11px;gap:6px}}
    .mini-feature b{{font-size:18px}}
    .hero-art{{min-height:340px;margin-top:0;border-radius:24px}}
    .phone{{width:190px;height:330px;padding:6px;border-width:6px;border-radius:32px}}
    .phone-screen{{border-radius:24px;font-size:82px}}
    .scan-box{{inset:48px 20px;border-radius:17px}}
    .disease-chip{{left:10px;right:10px;bottom:12px;padding:9px;font-size:9px}}
    .floating{{padding:8px 9px;font-size:9px;max-width:38%}}
    .floating.a{{top:18px;right:12px}}
    .floating.b{{left:12px;bottom:26px}}
    .login-shell{{margin-top:22px;padding:18px;border-radius:18px}}
    .login-title{{font-size:25px}}
    .feature-strip{{margin-top:24px;padding:18px 10px}}
    .feature-card{{min-height:0;padding:16px 10px}}
    .security-section{{padding:45px 0 35px}}
    .security-section h2{{font-size:clamp(1.9rem, 8vw, 2.5rem);line-height:1.05}}
    .step{{min-height:0;padding:16px}}
    .green-band{{margin:0 -1rem;padding:30px 1rem}}
    .green-band h2{{font-size:clamp(1.5rem,6vw,1.9rem)}}
}}
@media(max-width:420px){{
    .block-container{{padding-left:.75rem !important;padding-right:.75rem !important}}
    .brand-sub{{max-width:205px}}
    .hero-title{{font-size:clamp(2.25rem, 10vw, 2.8rem)}}
    .hero-art{{min-height:300px}}
    .phone{{transform:scale(.88)}}
    .floating.b{{bottom:15px}}
    .green-band{{margin:0 -.75rem;padding-left:.75rem;padding-right:.75rem}}
    .login-shell{{padding:15px}}
}}
</style>
""",
    unsafe_allow_html=True,
)

# A real anchor target makes Home links reliably return to the top.
st.markdown('<div id="top" style="height:1px"></div><div style="height:12px"></div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TOP HEADER
# -----------------------------------------------------------------------------
nav = st.container()
with nav:
    n1, n2, n3, n4, n5, n6 = st.columns([3.0, .9, 1.0, 1.0, 1.2, 1.0], gap="small")
    with n1:
        st.markdown(
            '<div class="brand-wrap"><div class="brand-mark">🌿</div><div><div class="brand-title">ATHARVADRISHTI</div><div class="brand-sub">AN INTELLIGENT AND EXPLAINABLE PLANT HEALTH ANALYSIS SYSTEM</div></div></div>',
            unsafe_allow_html=True,
        )
    with n2:
        st.markdown('<a class="nav-link" href="#top">⌂ Home</a>', unsafe_allow_html=True)
    with n3:
        st.markdown('<a class="nav-link" href="#features">▤ Features</a>', unsafe_allow_html=True)
    with n4:
        st.markdown('<a class="nav-link" href="#login">🔐 Login</a>', unsafe_allow_html=True)
    with n5:
        if st.button("📊 Dashboard", use_container_width=True, key="nav_dashboard"):
            st.switch_page("pages/5_Health_Dashboard.py")
    with n6:
        mode_label = "☾ Dark" if not is_dark else "☀ Light"
        if st.button(mode_label, use_container_width=True, key="nav_theme"):
            st.session_state["landing_theme"] = "dark" if not is_dark else "light"
            st.rerun()

# -----------------------------------------------------------------------------
# HERO
# -----------------------------------------------------------------------------
left, right = st.columns([1.02, .98], gap="large")
with left:
    st.markdown('<div class="hero-copy">', unsafe_allow_html=True)
    st.markdown('<span class="eyebrow">ATHARVADRISHTI · INTELLIGENT &amp; EXPLAINABLE PLANT HEALTH</span>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Smarter Insights for <span>Healthier Crops</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-text">ATHARVADRISHTI — An Intelligent and Explainable Plant Health Analysis System uses advanced AI to analyze plant health, explain visual evidence and help users make better crop-health decisions.</div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    with m1: st.markdown('<div class="mini-feature"><b>🌿</b><span>Detect Diseases<br>with AI</span></div>', unsafe_allow_html=True)
    with m2: st.markdown('<div class="mini-feature"><b>🛡</b><span>Get Expert<br>Guidance</span></div>', unsafe_allow_html=True)
    with m3: st.markdown('<div class="mini-feature"><b>↗</b><span>Improve Yield<br>&amp; Productivity</span></div>', unsafe_allow_html=True)
    st.write("")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("Start Now →", use_container_width=True, type="primary", key="hero_start"):
            st.switch_page("pages/1_AI_Scanner.py")
    with b2:
        st.markdown('<a class="nav-link" href="#features">Learn More ↓</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown(
        '''<div class="hero-art">
            <div class="floating a">⚡ AI-Powered Analysis</div>
            <div class="phone">
                <div class="phone-screen">🌿
                    <div class="scan-box"></div>
                    <div class="disease-chip">◒ &nbsp; Disease Detected · Tomato Early Blight</div>
                </div>
            </div>
            <div class="floating b">🧠 Explainable AI</div>
        </div>''',
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# LOGIN / SIGN-UP PANEL
# -----------------------------------------------------------------------------
st.markdown('<div class="login-shell" id="login">', unsafe_allow_html=True)
st.markdown('<div class="login-title">Welcome Back</div>', unsafe_allow_html=True)
st.markdown('<div class="login-sub">Login to your account to continue your plant-health workflow.</div>', unsafe_allow_html=True)
identity = st.text_input("Email Address", key="landing_identity", placeholder="Email Address", label_visibility="collapsed")
password = st.text_input("Password", type="password", key="landing_password", placeholder="Password", label_visibility="collapsed")
l1, l2 = st.columns(2)
with l1:
    if st.button("Login", use_container_width=True, type="primary", key="landing_login"):
        user, error = authenticate(identity, password)
        if error:
            st.error(error)
        elif user:
            session_login(user)
            st.success("Login successful.")
            st.switch_page("pages/1_AI_Scanner.py")
with l2:
    if st.button("Sign Up", use_container_width=True, key="landing_signup"):
        st.switch_page("pages/2_Sign_Up.py")
st.markdown('<div class="security-note">🛡️ Supabase Auth · Secure login sessions · Private scan history</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FEATURES
# -----------------------------------------------------------------------------
st.markdown('<div class="feature-strip" id="features">', unsafe_allow_html=True)
fcols = st.columns(6)
features = [
    ("🧠", "AI Disease Detection", "Identify plant diseases with AI."),
    ("🛡️", "Secure & Reliable", "Layered account verification."),
    ("🌱", "Farm Management", "Manage farms and crops."),
    ("📋", "Expert Guidance", "Observation-focused guidance."),
    ("📈", "Analytics & Reports", "Track crop health trends."),
    ("📱", "Multi-Device Access", "Use the platform anywhere."),
]
for c, (icon, title, desc) in zip(fcols, features):
    with c:
        st.markdown(f'<div class="feature-card"><div class="feature-icon">{icon}</div><h3>{title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SECURITY FLOW
# -----------------------------------------------------------------------------
st.markdown('<div class="security-section">', unsafe_allow_html=True)
st.markdown('<span class="eyebrow">SECURE ACCESS</span>', unsafe_allow_html=True)
st.markdown('<h2>Secure Access & Personal History</h2>', unsafe_allow_html=True)
st.markdown('<p>Sign in securely and keep your plant-health scan history connected to your own account.</p>', unsafe_allow_html=True)
steps = st.columns(4)
step_data = [
    ("1", "Sign Up / Login", "Create your account or securely sign in."),
    ("2", "Private Scan History", "Keep your scans connected to your own account."),
    ("3", "Health Dashboard", "Review your recent plant-health analyses."),
    ("4", "Account Control", "Log out when you finish your session."),
]
for c, (num, title, desc) in zip(steps, step_data):
    with c:
        st.markdown(f'<div class="step"><strong>{num}. {title}</strong><p>{desc}</p><div class="mini">✓ Security step</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="green-band"><h2>Together for a Greener Tomorrow</h2><p>Better technology. Healthier crops. Stronger farmers.</p></div>', unsafe_allow_html=True)
st.markdown('<div class="footer">© 2026 ATHARVADRISHTI · An Intelligent and Explainable Plant Health Analysis System</div>', unsafe_allow_html=True)

