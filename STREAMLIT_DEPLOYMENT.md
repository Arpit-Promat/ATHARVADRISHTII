# Streamlit Community Cloud deployment

## Required app configuration

Use these exact values in Streamlit Community Cloud:

- **Repository:** `Arpit-Promat/ATHARVADRISHTII`
- **Branch:** `main`
- **Main file path / entrypoint:** `streamlit_app.py`
- **Dependency file:** root `requirements.txt`
- **Python:** 3.12 (the Community Cloud default documented at the time of this guide)

Do not select `app.py`: that file is the Flask API/backend, not the Streamlit interface. Do not select `pages/1_AI_Scanner.py` as the main entrypoint if you want the complete landing page and navigation. The scanner is a multipage destination.

## Streamlit Secrets

In the deployed app, open **Manage app → Settings → Secrets** and configure:

```toml
SUPABASE_URL = "https://YOUR_PROJECT_REF.supabase.co"
SUPABASE_ANON_KEY = "YOUR_SUPABASE_PUBLISHABLE_OR_LEGACY_ANON_KEY"
```

Use the publishable/anon key only. Never put a Supabase service-role or secret key in a browser-facing Streamlit app. Do not commit real secrets to Git.

For immediate sign-up sessions in the current temporary workflow, turn off **Confirm email** in Supabase Authentication settings. Re-enable email confirmation before treating the app as a public production service.

## Per-user scan history

Run `supabase/scan_history_migration.sql` once in the Supabase SQL Editor. It creates/extends `public.scan_history`, adds the session-key/status/top-predictions columns, and enables per-user Row Level Security policies.

## Model artifacts

The `.keras` artifacts are stored with Git LFS. Streamlit Community Cloud supports Git LFS, so the deployed checkout should contain the real model files rather than the small text pointer files. The scanner now detects an unresolved LFS pointer and displays an actionable error instead of a generic Keras load failure.

## Deploy updates

The Streamlit app is connected to GitHub. Commits pushed to the configured branch are automatically deployed by Community Cloud. If the landing page does not appear after the latest commit, check that the app's **Main file path** is `streamlit_app.py`, then reboot the app and inspect its Cloud logs.

## Local run

From the repository root:

```bash
streamlit run streamlit_app.py
```

Run the Flask API separately only when needed:

```bash
python app.py
```
