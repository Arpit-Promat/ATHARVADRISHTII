# India Vegetable Leaf Classifier

ATHARVADRISHTI now has a separate training path for vegetable-leaf classification. It is kept separate from the PlantDoc, Mango, FruitLeaf6, Wheat and Rice models so those models and their class-index mappings are not overwritten.

## Important: catalog coverage is not trained-model coverage

The India-focused catalog currently lists these 53 crop groups:

Amaranth, Ash gourd, Beetroot, Bitter gourd, Bottle gourd, Brinjal, Broccoli, Cabbage, Capsicum, Carrot, Cauliflower, Cluster beans, Colocasia, Cowpea, Cucumber, Curry leaf, Drumstick, Fenugreek, Garlic, Gherkin, Green chilli, Ivy gourd, Lablab bean, Lesser yam, Lettuce, Lotus stem, Mint, Mustard greens, Okra, Onion, Pea, Pointed gourd, Potato, Pumpkin, Radish, Raw banana, Ribbed celery, Ridge gourd, Round chilli, Snake gourd, Spinach, Sponge gourd, Spring onion, Sweet corn, Sweet potato, Tapioca, Tinda, Tomato, Turmeric, Winged bean, Yam, Zucchini, Ginger, Coriander.

This is a practical India-focused crop scope based on public Indian agricultural commodity and horticulture references, not a claim that every local vegetable, wild edible, or cultivar in India is covered. The e-NAM commodity list and APEDA vegetable references include a wide range of vegetables; crop availability and naming vary by region.

**A crop is not supported by the neural network just because it appears in this catalog.** It becomes a trained class only after correctly labelled leaf images are collected, split, trained, validated and included in the saved class-name file.

## Current trained vegetable coverage

The existing PlantDoc 38-class classifier includes 16 vegetable-related labels across four crop groups:

- Tomato — 10 labels (healthy plus disease/pest classes)
- Potato — 3 labels (healthy, early blight, late blight)
- Bell pepper / capsicum — 2 labels (healthy, bacterial spot)
- Squash — 1 label (powdery mildew)

It does not currently provide trained leaf-disease coverage for the rest of the India-focused catalog. The scanner displays this distinction instead of pretending the catalog is a trained model.

## Dataset folder structure

Collect real leaf photographs and create matching class folders in both splits:

```text
dataset/
└── VegetableLeaves/
    ├── train/
    │   ├── Tomato___healthy/
    │   ├── Tomato___Early_blight/
    │   ├── Brinjal___healthy/
    │   ├── Brinjal___Phomopsis_blight/
    │   ├── Okra___healthy/
    │   └── Okra___Yellow_vein_mosaic/
    └── val/
        ├── Tomato___healthy/
        ├── Tomato___Early_blight/
        ├── Brinjal___healthy/
        ├── Brinjal___Phomopsis_blight/
        ├── Okra___healthy/
        └── Okra___Yellow_vein_mosaic/
```

Use canonical crop names from `vegetable_leaf_support.py` as the part before `___`. Use the exact same class folder names in train and val. Disease names must be verified for that crop; do not copy a tomato disease label onto another vegetable unless it is genuinely applicable and correctly labelled.

The default trainer requires all catalog crops and at least two genuine classes per crop (for example, healthy plus one verified disease). To train a pilot with only the crops currently available, explicitly run:

```bash
python train_vegetable_leaf.py --allow-partial
```

A pilot model is limited to the crops/classes in its class-name file. It must not be advertised as supporting all vegetables.

When a balanced full dataset is ready, run:

```bash
python train_vegetable_leaf.py --epochs 20
```

The script writes:

- `models/vegetable_leaf_model.keras`
- `models/vegetable_leaf_class_names.json`

The Streamlit scanner automatically adds **India Vegetable Leaf Classifier** to its model selector only when both trained artifacts exist. It uses the same RGB [0, 1] preprocessing as the training script.

## Public dataset leads for building the full dataset

These are candidate sources to curate into the folder structure above. They are **not automatically downloaded or included in this repository**, and their published class labels should be reviewed before training.

| Source | Vegetable coverage / size | Notes |
|---|---|---|
| [Digital Green Crop Disease Images](https://huggingface.co/datasets/DigiGreen/Crop_Disease_Images) | Indian field annotations; includes chilli, brinjal, cauliflower, potato, pea, pumpkin, cowpea and other crops; 1,026 rows | Dataset card states CC BY 4.0. Review annotation quality and image availability; not every row is a clean single-leaf image. |
| [Brinjal leaf dataset — Mendeley Data](https://data.mendeley.com/datasets/c39p3k87g2/2) | 850 original Rajasthan field images; healthy, Phomopsis blight and little-leaf classes | Dataset page states CC BY 4.0 and provides metadata with original-level splits. Use the original images and respect its split metadata; do not randomly split augmented variants. |
| [Okra disease dataset paper — PubMed](https://pubmed.ncbi.nlm.nih.gov/40687361/) | 2,500 India field images; healthy plus five disease classes | The paper describes real-field Indian images. Check the linked dataset's own access and license terms before reuse; the article is open access for non-commercial use. |
| [Comprehensive Vegetable Leaf Disease Image Collection — Mendeley](https://data.mendeley.com/datasets/rh8c5tgg5k/1) | 1,923 images across broccoli, cabbage, cauliflower and turnip | Useful additional cole-crop coverage; check the dataset page license and verify source/split metadata before merging. |

Do not treat published benchmark accuracy as ATHARVADRISHTI's accuracy. Re-train and evaluate on a held-out set that is independent of the source dataset's training images.

## Data quality checklist

- Capture leaves from multiple farms/fields, districts, seasons and phones.
- Include healthy leaves and expert-confirmed disease classes for each crop.
- Keep near-duplicate photos of the same plant in only one split to avoid data leakage.
- Include natural variation in lighting, background, leaf age and disease severity.
- Remove blurred, mislabelled, non-leaf and mixed-crop images.
- Keep a record of source, crop, disease label, date and expert/extension-worker verification.
- Review per-class precision, recall, confusion matrix and independent field-test performance before deployment.

Do not present a model confidence score as a guaranteed diagnosis. The model is a decision-support tool; farmers should confirm important treatment decisions with an agricultural expert.

## Official reference points

- e-NAM commodity list: https://enam.gov.in/commodity/commodity-list
- APEDA fresh fruits and vegetables: https://apeda.gov.in/FreshFruitsAndVegetables
- ICAR Kharif agro-advisories: https://icar.gov.in/sites/default/files/Circulars/ICAR-En-Kharif-Agro-Advisories-for-Farmers-2025.pdf
