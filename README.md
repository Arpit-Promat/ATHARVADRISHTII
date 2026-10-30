# ATHARVADRISHTI — An Intelligent and Explainable Plant Health Analysis System

An AI-powered plant health analysis project built with Flask, Streamlit, TensorFlow and MobileNetV2. The system combines image-based plant-condition classification with explainable AI using SHAP.

## Project Overview

**ATHARVADRISHTI** is designed to analyze plant leaf images, identify the most likely plant condition, report prediction confidence and provide visual explanations of the model's decision.

The application includes:
- General plant-condition classification
- Mango-specific classification
- Leaf / non-leaf image validation
- Confidence and prediction-margin checks
- SHAP-based visual explainability
- Streamlit interface with authentication
- Flask APIs for management, feedback, analytics and decision support

## Dataset

The project uses the **PlantDoc dataset** as one of its underlying training/data sources. The dataset itself keeps its original name; the application and product are now branded as **ATHARVADRISHTI**.

Download the required dataset and place the training class folders inside:

`dataset/train/`

Example:

`dataset/train/`
```
├── Tomato_Early_blight/
│   ├── image1.jpg
│   └── image2.jpg
├── Tomato_Late_blight/
│   └── ...
└── Apple_Scab/
    └── ...
```

The folder name becomes the predicted class name.

## Create virtual environment

Windows:

```
python -m venv venv
venv\\Scripts\\activate
```

## Install libraries

```
pip install -r requirements.txt
```

## Train the model

```
python train.py
```

The trained PlantVillage general model is saved as:

`models/plantdoc_model.keras` (legacy filename; the training data is PlantVillage, not PlantDoc).

## Run the application

For the Streamlit product interface:

```
streamlit run streamlit_app.py
```

For the Flask API/backend:

```
python app.py
```

## Command-line prediction

```
python predict.py path/to/leaf.jpg
```

## Project Name

**ATHARVADRISHTI**

*An Intelligent and Explainable Plant Health Analysis System*

## Important

The repository contains the application code, but not the large PlantDoc image dataset itself. Add the required dataset under `dataset/train/` before training.


## Configure Streamlit email verification

The Streamlit-native signup flow requires email verification. SMS verification is optional; SMS-based 2FA requires Twilio credentials.

In Streamlit Community Cloud, open your app's **Settings → Secrets** and add SMTP credentials. For Gmail, first enable 2-Step Verification and create a Google App Password. Never use or commit your normal Gmail password.

```toml
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-gmail-address@gmail.com"
SMTP_PASSWORD = "your-16-character-google-app-password"
SMTP_USE_TLS = "1"
EMAIL_FROM = "your-gmail-address@gmail.com"
```

After saving Secrets, reboot/restart the deployed app and use **Verify → Resend codes** for an existing account. Secrets are deployment settings and cannot be set through this GitHub repository.

Optional SMS / SMS-based 2FA settings:

```toml
TWILIO_ACCOUNT_SID = "your-twilio-account-sid"
TWILIO_AUTH_TOKEN = "your-twilio-auth-token"
TWILIO_FROM_NUMBER = "+1..."
```

Do not enable `AUTH_DEV_SHOW_OTP=1` on a public deployment; it is only for local development.
