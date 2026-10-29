# Supabase setup for ATHARVADRISHTI

## 1. Configure Supabase Auth
- In Supabase Dashboard, open Authentication settings.
- For the temporary development setup, turn off **Confirm Email**.
- Use email + password for sign-up and login. Mobile number is saved as optional profile metadata only.
- Before a public production launch, turn email confirmation back on and configure a verified email sender.

## 2. Configure local secrets
Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and replace the placeholders:
```toml
SUPABASE_URL = "https://YOUR_PROJECT_REF.supabase.co"
SUPABASE_ANON_KEY = "YOUR_SB_PUBLISHABLE_KEY_OR_LEGACY_ANON_KEY"
```
The key may start with `sb_publishable_` or be the legacy `anon` key. Never use `sb_secret_` or `service_role`.

## 3. Configure Streamlit Community Cloud
Open the deployed app's **Settings → Secrets** and add the same two TOML entries there. Keep local and cloud secrets separate.

## 4. Apply the database schema
Run `supabase/scan_history_migration.sql` in the Supabase SQL Editor. It adds the columns used by the current scanner and creates per-user RLS policies. Do not disable RLS.

## 5. Install and run locally
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Notes
- Authentication sessions are kept in Streamlit session state.
- Scan-history reads and writes use the authenticated Supabase client and are restricted by Row Level Security.
- This integration preserves the existing page styling and scanner prediction UI.
