# Streamlit Community Cloud deployment

## Required app configuration

Use these exact values in Streamlit Community Cloud:

- **Repository:** `Arpit-Promat/ATHARVADRISHTII`
- **Branch:** `main`
- **Main file path / entrypoint:** `streamlit_app.py`
- **Dependency file:** root `requirements.txt`
- **Python:** 3.12 (the Community Cloud default documented at the time of this guide)

Do not select `app.py`: that file is the Flask API/backend, not the Streamlit interface. Do not select `pages/1_AI_Scanner.py` as the main entrypoint if you want the complete landing page and navigation. The scanner is a multipage destination.

## Scanner access

The active plant-detection workflow does not require Supabase credentials, account creation, or login. The landing page opens the scanner directly. Do not add authentication secrets just to use plant detection.

## Scan history

Per-user scan-history SQL and account modules remain in the repository for possible future use, but they are not part of the active detection-only workflow.

## Model artifacts

The classifier and leaf-detector model files are stored with Git LFS. On first scan, the application attempts to resolve each public LFS pointer through GitHub's LFS batch API, downloads the object to a temporary cache, and verifies its declared byte size and SHA-256 digest before loading it. If the LFS object cannot be obtained or verified, the scanner stops with an explicit error rather than producing a fabricated diagnosis.

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
