# Neon PostgreSQL setup for ATHARVADRISHTI

The Streamlit-native account verification, user records, OTP challenges, and Streamlit scan history use `DATABASE_URL`. The Flask/SQLAlchemy API also uses `DATABASE_URL`. They can share one Neon PostgreSQL database; each subsystem creates its own tables.

## 1. Create a Neon database

1. Sign in at https://neon.tech and create a project.
2. Open the project's **Connect** panel.
3. Copy the PostgreSQL connection string. Prefer the pooled connection string for a hosted web app if Neon offers it.
4. Keep the SSL requirement (normally `sslmode=require`). Do not commit the connection string to GitHub or paste it into a public issue.

The app supports `postgresql://...`, `postgres://...`, and `postgresql+psycopg://...` connection URL forms.

## 2. Configure Streamlit Community Cloud

Open the deployed app in Streamlit Community Cloud, open **Settings → Secrets**, and add the following TOML values, replacing the placeholders with your actual provider credentials:

```toml
DATABASE_URL = "postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require"

# Required for real email verification
SMTP_HOST = "smtp.your-email-provider.com"
SMTP_PORT = "587"
SMTP_USE_TLS = "1"
SMTP_USERNAME = "your-smtp-username"
SMTP_PASSWORD = "your-smtp-password"
EMAIL_FROM = "your-verified-sender@example.com"

# Required for real SMS verification (Twilio)
TWILIO_ACCOUNT_SID = "your-twilio-account-sid"
TWILIO_AUTH_TOKEN = "your-twilio-auth-token"
TWILIO_FROM_NUMBER = "+15551234567"
```

Save secrets and reboot/redeploy the Streamlit app. Never enable `AUTH_DEV_SHOW_OTP = "1"` in production.

## 3. Configure Render only if the Flask API is still used

In the Render service's **Environment** settings, set `DATABASE_URL` to the same Neon connection string. The code now selects the installed psycopg 3 driver for SQLAlchemy. If Render is no longer used by any part of the application, you do not need to configure it there.

## 4. Verification delivery

Neon stores user records and OTP challenges; it does **not** deliver OTP messages. Real email OTP requires SMTP credentials, and real SMS OTP requires a configured SMS provider such as Twilio. Without those credentials, the app will show a configuration error instead of silently pretending the code was sent.

For a local-only demo, set `AUTH_DEV_SHOW_OTP = "1"` in local Streamlit secrets; codes will be shown in the app for testing. Remove/disable this before deployment.

## 5. Existing data

Changing `DATABASE_URL` points the app at a new database; it does not copy old records automatically. To preserve existing Render PostgreSQL users/scans, export the old database and import it into Neon before changing the production URL. Take a backup first. The Streamlit-native tables (`streamlit_users`, `streamlit_auth_challenges`, and `streamlit_scan_history`) are separate from the Flask tables (`users`, `scans`, `farms`, `crops`, and related tables), even when they share the same Neon database.
