# ATHARVADRISHTI Authentication Starter

This folder is deliberately isolated from the existing application. It does **not** replace the repository's live entry point.

## Contents
- `models.py`: PostgreSQL SQLAlchemy models.
- `auth.py`: password rules/hash, registration, verification tokens, login lockout, TOTP helpers and HMAC cookie primitives.
- `email_service.py`: Resend email sender.
- `streamlit_app.py`: standalone demo UI; run only for local/staging testing.
- `pages/2_Settings.py`: optional TOTP settings example.
- `scripts/init_db.py`: database schema initialization.
- `tests/`: starter tests.
- `.github/workflows/`: CI and manual DB init workflows (scoped under this folder; GitHub Actions only discovers workflows at repository-root .github/workflows, so copy them there deliberately if desired).

## Secrets
Configure these in Streamlit Cloud → App settings → Secrets, never in Git:
```toml
DATABASE_URL = "postgresql+psycopg2://USER:PASSWORD@HOST/DB?sslmode=require"
APP_SECRET_KEY = "REPLACE_WITH_FERNET_KEY"
RESEND_API_KEY = "re_REPLACE_ME"
APP_BASE_URL = "https://your-app.streamlit.app"
ADMIN_EMAIL = "admin@example.com"
REQUIRE_EMAIL_VERIFICATION = "false"
EMAIL_FROM = "ATHARVADRISHTI <noreply@your-verified-domain.com>"
```
Generate a Fernet key in Termux:
`python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
Use a verified sender domain in Resend. Never commit real secrets.

## Run in Termux
From repository root:
```bash
cd auth_starter
pip install -r requirements.txt
pytest -q
streamlit run streamlit_app.py
```

For DB initialization, run `python scripts/init_db.py` with `DATABASE_URL` set in the environment. This folder's workflow YAML files are examples; GitHub only runs workflows stored under repository-root `.github/workflows/`.

## Security status / limitations
This is a starter, not production-ready. Rate limiting is process-local and resets on restart. HMAC cookie signing helpers are provided, but browser cookie transport and checking the cookie nonce against the database are **not implemented**; the demo uses Streamlit session state only. Tests are smoke tests, not PostgreSQL integration tests. Account deletion request flow, password-reset flow, and complete audit coverage remain to be implemented. Review and test on staging before real-user use.
