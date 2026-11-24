# Dedicated Guava Leaf Classifier

This training path is isolated from the existing PlantDoc, Mango, FruitLeaf6, Wheat and Rice models. It does not modify their weights or class maps.

## Dataset candidate

A candidate public dataset is **IDGLDD: Guava Leaf Diseases and Pest Damage for Five-Class Classification**, Mendeley Data version 3. Its page describes 4,715 guava leaf images across five classes (Anthracnose, Caterpillar damage, Healthy, Red rust and Spiraling whitefly), with 943 images per class, field collection in Bangladesh, specialist labelling and a CC BY 4.0 licence.

Dataset page: https://data.mendeley.com/datasets/46spm4z4d3/3

Before use, download the original images and inspect the archive, labels, duplicate images, licence/attribution requirements and any supplied split metadata. Prefer original images over augmented copies. Do not split near-duplicate or augmented versions across train, validation and test. Dataset geography and backgrounds may differ from Indian field photos, so independent Indian guava-leaf testing is required before deployment.

## Required folder structure

Create the same class folders in all three splits. Example labels should exactly match the verified source annotations:

```text
dataset/GuavaLeaves/
  train/
    Guava___Anthracnose/
    Guava___Caterpillar_damage/
    Guava___healthy/
    Guava___Red_rust/
    Guava___Spiraling_whitefly/
  val/
    (same five folders)
  test/
    (same five folders)
```

Do not rename a source class to a different disease name. If the downloaded dataset uses different official labels, use those exact labels after prefixing each with `Guava___`.

## Train

Install the repository requirements, then run:

```bash
python train_guava_leaf.py
```

The script trains a separate MobileNetV2 classifier using RGB values scaled to [0, 1], verifies matching class folders across train/validation/test, selects checkpoints using validation loss, and reports held-out test accuracy and per-class recall.

Outputs:
- `models/guava_leaf_model.keras`
- `models/guava_leaf_class_names.json`

The scanner exposes the Guava model only when both output files exist. The model is a guava-only classifier; users must select it only for guava leaves.

## Release gate

Do not deploy or claim reliable guava diagnosis based only on training accuracy or confidence. Review the confusion matrix/per-class precision and recall, inspect false predictions, and test on separate guava photos collected in India under natural backgrounds, lighting and phone-camera conditions. Confirm disease labels with an agricultural expert. Until that validation is complete, treat outputs as experimental decision support, not a confirmed diagnosis.
