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

## Dataset and reproducible training

The root `train.py` script expects a **PlantVillage-style** directory layout. It does not read from `dataset/train/` as the previous instructions stated.

Place matching class folders in both locations:

```text
dataset/
└── PlantVillage/
    ├── train/
    │   ├── Apple___Apple_scab/
    │   ├── Apple___healthy/
    │   └── ...
    └── val/
        ├── Apple___Apple_scab/
        ├── Apple___healthy/
        └── ...
```

Training and validation folders must contain the same class-folder names. The script derives class indices from the training folder and checks that the validation mapping matches. It writes the resulting ordered class map to `models/class_names.json`.

**Important:** the class-name JSON in the repository contains PlantVillage-style labels. Do not describe a model as trained on PlantDoc unless the actual training dataset and model provenance confirm that. Dataset names, class maps and model weights must always refer to the same training run.

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

The trained general model is saved as:

`models/plantdoc_model.keras`

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


## India vegetable-leaf expansion

The scanner now distinguishes the vegetable classes already trained in the PlantDoc model from the broader India-focused crop catalog. A separate MobileNetV2 training pipeline is available in `train_vegetable_leaf.py`; see [VEGETABLE_LEAF_TRAINING.md](VEGETABLE_LEAF_TRAINING.md) for dataset structure, crop scope, validation requirements and deployment steps. The dedicated model is offered in the scanner only after its trained `.keras` file and matching ordered class-name JSON are present.

## Streamlit Community Cloud deployment

See [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md) for the exact repository, branch, and main-file settings. The Streamlit entrypoint is `streamlit_app.py`; `app.py` is the separate Flask API/backend. Configure Supabase credentials in Streamlit Cloud Secrets, never in Git.

## Streamlit authentication configuration

The current Streamlit entrypoint (`streamlit_app.py`) uses **Supabase Auth** through `app_supabase_auth.py`. Configure only the Supabase project URL and publishable/legacy anon key in Streamlit Community Cloud Secrets, as documented in [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md).

`streamlit_native_auth.py` is a separate legacy/native authentication implementation and is not used by the current Streamlit login flow. Its SMTP/Twilio settings do not configure Supabase authentication. Never commit credentials, service-role keys or SMTP passwords to Git.
