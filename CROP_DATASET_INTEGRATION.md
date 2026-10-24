# Integrating Wheat, Paddy/Rice, and Sugarcane datasets

This repository includes a safe inspection script and a local training script for Wheat disease and Rice pest classifiers. The trained models are **not** part of the repository yet; you must train them locally using your extracted datasets.

## Why training is not included yet

- The extracted dataset folder paths and class labels are on the developer's computer and are not accessible from GitHub automatically.
- The current Sugarcane download described in the project conversation contains healthy leaves only. Healthy-only images cannot train a multi-disease Sugarcane classifier.
- We must verify the actual class folders and image counts before making a training/validation split or changing the deployed model registry.

## Inspect the local datasets

From the repository root on Windows, activate the project's virtual environment if desired, then run:

```powershell
python scripts/inspect_crop_datasets.py
```

When prompted, paste the full path to each extracted Wheat, Paddy/Rice, and Sugarcane folder. The script only reads the folders and reports image counts by subfolder; it does not modify or upload any data.

## Train the Wheat classifier

First pull the latest repository code:

```powershell
git pull origin main
```

Train only Wheat first:

```powershell
.\.venv\Scripts\python.exe scripts\train_crop_models.py --model wheat
```

When prompted, enter the extracted root folder, for example `C:\Users\Dell\Downloads\Crop Dataset`. The script selects the Wheat Healthy, Septoria, and Stripe Rust folders and ignores the Tomato classes. It uses the source train folders, makes a validation split, and evaluates on matching Wheat test folders when available.

The output files should be:

- `models/wheat_model.keras`
- `models/wheat_class_names.json`

## Train the Rice pest classifier

After Wheat training completes, run:

```powershell
.\.venv\Scripts\python.exe scripts\train_crop_models.py --model rice-pest
```

When prompted, enter your extracted `Pest_V2` folder, for example `C:\Users\Dell\Downloads\Pest_V2`. The script groups nested adult/egg/larva folders under each top-level pest name, so the model predicts the pest category rather than the life stage.

The output files should be:

- `models/rice_pest_model.keras`
- `models/rice_pest_class_names.json`

The script uses MobileNetV2 pretrained weights, so the first run may need internet access to download those weights. It trains locally and does not upload your dataset. Check the validation metrics and the separate Wheat test result before using either model.

## Before app integration

Do not change `model_registry.py` or the deployed app yet. First confirm both local training runs finish and that the four output files above exist. Then the model loading and Streamlit interface can be integrated and tested.

Keep the Sugarcane healthy-only dataset separate until labelled diseased classes are obtained. Do not commit the raw 3 GB dataset to GitHub; large model artifacts should use an approved artifact store or Git LFS when appropriate.

## Resource guidance

For an 8 GB RAM laptop, start with 224×224 images and batch size 8, and use streaming data loaders rather than loading the entire dataset into memory.
