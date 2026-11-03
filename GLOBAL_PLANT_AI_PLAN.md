# Global Plant AI upgrade (ATHARVADRISHTI)

## Reality check
There is no image dataset containing every plant species on Earth. This upgrade expands coverage to the species present in the selected, licensed training data. Do not describe it as identifying every plant or every disease.

## Recommended data sources
1. **Plant identification:** [plantNaturalist-500k](https://huggingface.co/datasets/anhaltai/plantNaturalist500k) — 500,909 real-world images across 2,491 plant species; dataset card reports 227 GB and CC BY-NC 4.0. Do not download all 227 GB to a normal laptop. Start with a curated subset (for example, 50–100 species with enough images) and preserve attribution/licence metadata. Verify current access and dataset card before downloading.
2. **Plant taxonomy / names:** iNaturalist / GBIF. Use metadata to normalize scientific names and common names. iNaturalist photos have per-image licences; retain creator, licence and source fields. Do not assume all images are reusable.
3. **Disease detection:** PlantVillage plus the project's existing PlantDoc, FruitLeaf6, Mango, Wheat, Rice and Sugarcane datasets. Keep the disease task separate from species identification.

## Local folder format
Place only images you are permitted to use in these folders:

```
datasets/
  plant_identification/
    train/<scientific_name>/*.jpg
    val/<scientific_name>/*.jpg
    test/<scientific_name>/*.jpg
  plant_disease/
    train/<plant___disease>/*.jpg
    val/<plant___disease>/*.jpg
    test/<plant___disease>/*.jpg
```

Split by observation/specimen, not by individual photo, to prevent near-duplicate leakage. Remove corrupt files and duplicates. Keep a balanced number of examples per class. Keep a CSV with image path, scientific name, common name, source, creator, licence and observation ID.

## Train locally
Install dependencies in the project's active virtual environment:
```powershell
python -m pip install tensorflow pillow
``

Train the species model:
```powershell
python training/train_global_classifier.py --task plant --data datasets/plant_identification --epochs 10 --batch-size 8
``

Train the disease model:
```powershell
python training/train_global_classifier.py --task disease --data datasets/plant_disease --epochs 10 --batch-size 8
``

The script uses ImageNet-pretrained MobileNetV2 and saves separate model and class-name files in models/. It does not modify or replace existing models.

## Evaluation and product behaviour
- Evaluate on the untouched test split; report top-1 accuracy, macro precision/recall/F1 and per-class support.
- Show "Unknown / not confidently recognized" when confidence is below a threshold calibrated on validation data.
- Disease prediction must be limited to supported plant/disease classes. Do not claim universal disease diagnosis.
- Test on phone photos from outside the training datasets. PlantNet/iNaturalist-style real-world images are important because PlantVillage backgrounds are controlled.
- Integrate only after checking preprocessing, class order, model loading and real-image performance.

## Honest presentation wording
"ATHARVADRISHTI is being extended with a global plant-identification pipeline using licensed, real-world species imagery, alongside a separate plant-disease classifier. Coverage depends on the species and disease classes represented in the training data."
