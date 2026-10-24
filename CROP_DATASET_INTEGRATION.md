# Integrating Wheat, Paddy/Rice, and Sugarcane datasets

This repository update adds a safe inspection script for the three locally extracted datasets. It does **not** add trained crop models yet.

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

## Next steps after inspection

1. Review the class names and counts printed by the script.
2. Confirm that each disease class has labelled images. Keep the Sugarcane healthy-only dataset separate until diseased classes are obtained.
3. Create a reproducible train/validation split only if the source dataset does not already include one.
4. Train and evaluate crop-specific models; do not treat validation accuracy as test accuracy.
5. Add each verified model and its class-name JSON to `model_registry.py` only after the model artifact exists and the scanner has been tested against it.
6. Commit code and small configuration/label files. Do not commit the raw 3 GB dataset to GitHub. Large model artifacts should use an approved artifact store or Git LFS when appropriate.

## Resource guidance

For an 8 GB RAM laptop, start with 224×224 images and batch size 8, and use streaming data loaders rather than loading the entire dataset into memory.
