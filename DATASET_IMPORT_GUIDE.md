# Import the downloaded 6-crop Fruit & Leaf dataset

ATHARVADRISHTI now includes a local import/audit script for the six-crop Fruit and Leaf dataset. Large images and ZIP archives stay on your computer; do not upload them to GitHub.

## 1. Keep the downloaded ZIPs

Create this local folder in the repository:

```text
data/raw/fruit_leaf_6crop/
```

Copy both ZIPs there. Do not rename or delete them yet. Check their full filenames and dataset release/version before extracting. If they are two versions rather than split parts, keep them separate.

## 2. Extract locally

Extract into a separate folder, for example:

```text
data/raw/fruit_leaf_6crop/extracted/
```

Preserve the original class folders and source metadata. Do not combine folders with identical-looking names until their meanings are checked.

## 3. Install image dependency if needed

```bash
pip install Pillow
```

## 4. Generate an inventory manifest

Run from the repository root (Windows PowerShell):

```powershell
python scripts/import_fruit_leaf_dataset.py --input "data/raw/fruit_leaf_6crop/extracted" --dataset-id mendeley_fruit_leaf_6crop
```

The script creates:

```text
data/metadata/mendeley_fruit_leaf_6crop_import_manifest.csv
```

It records image paths, original folder label, candidate crop and plant part, SHA-256, exact duplicate flags, image validity, and review status. It does not move, rename, delete, upload, or train on images.

## 5. Review before training

The current general model has leaf classes for Apple and Citrus, and a separate Mango leaf model. Banana and Guava are new crop candidates. The downloaded dataset may also include fruit images, which the current leaf classifiers do not yet classify.

The script's label guesses are only candidates. Check the CSV for UNKNOWN crops, unknown plant parts, review_required, and needs_label_review; verify class meaning and license/source records before canonical mapping and training.

## Privacy, storage and Git

The repository's .gitignore excludes data/raw/* and generated import/audit manifests. Dataset images are not added to GitHub by this script. The source repository records code and instructions, not your local dataset files.
