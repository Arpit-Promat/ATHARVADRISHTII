# ATHARVADRISHTI Auth Starter Kit

This is an isolated starter folder. It is intentionally on branch `auth-starter-kit`, not `main`, so it will not trigger your live Streamlit deployment before review.

## Setup
Configure Streamlit Cloud secrets: `DATABASE_URL`, `APP_SECRET_KEY` (Fernet key), `RESEND_API_KEY`, `APP_BASE_URL`, `ADMIN_EMAIL`, `EMAIL_FROM`, and `REQUIRE_EMAIL_VERIFICATION`. Never commit real secrets.

Generate a Fernet key with:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Set up Neon PostgreSQL, verify a sending domain in Resend, and add GitHub Actions secret `DATABASE_URL` before manually running the database-init workflow.

## Files
- `models.py`: SQLAlchemy models
- `auth.py`: password, registration, verification, lockout and TOTP helpers
- `email_service.py`: Resend email service
- `streamlit_app.py`: standalone example UI
- `pages/2_Settings.py`: optional TOTP setup
- `scripts/init_db.py`: create tables
- `tests/`: initial unit tests

## Important
This is a starter, not production-ready yet. Cookie-signing primitives are not wired to browser cookie transport; rate limiting is process-local; included tests are basic smoke tests and do not cover PostgreSQL lockout/token expiry end-to-end. Review and test on staging before merging. Do not replace the current app entrypoint until integration is tested.