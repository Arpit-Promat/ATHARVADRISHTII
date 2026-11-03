"""India-focused vegetable catalog and trained-class coverage helpers.

The catalog is a practical crop scope for the vegetable-leaf roadmap. India has
many regional vegetables and cultivars; catalog membership alone does NOT mean
a crop has been trained. A class is supported only when matching labelled leaf
images are present in the trained model metadata.
"""
from __future__ import annotations

# Preserve the exact labels currently present in the deployed 38-class model.
VEGETABLE_CLASS_GROUPS = {
    "Tomato": (
        "Tomato___Bacterial_spot",
        "Tomato___Early_blight",
        "Tomato___Late_blight",
        "Tomato___Leaf_Mold",
        "Tomato___Septoria_leaf_spot",
        "Tomato___Spider_mites Two-spotted_spider_mite",
        "Tomato___Target_Spot",
        "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
        "Tomato___Tomato_mosaic_virus",
        "Tomato___healthy",
    ),
    "Potato": (
        "Potato___Early_blight",
        "Potato___Late_blight",
        "Potato___healthy",
    ),
    "Bell Pepper": (
        "Pepper,_bell___Bacterial_spot",
        "Pepper,_bell___healthy",
    ),
    "Squash": (
        "Squash___Powdery_mildew",
    ),
}

# India-focused vegetable leaf catalog. Common regional names are aliases,
# not separate ML classes. Dataset class names should use canonical crop names.
INDIAN_VEGETABLE_CROPS = {
    "Amaranth": ("chaulai", "red amaranth", "green amaranth"),
    "Ash gourd": ("winter melon", "petha"),
    "Beetroot": ("beet",),
    "Bitter gourd": ("karela",),
    "Bottle gourd": ("lauki",),
    "Brinjal": ("eggplant", "aubergine", "baingan"),
    "Broccoli": (),
    "Cabbage": (),
    "Capsicum": ("bell pepper", "sweet pepper", "shimla mirch"),
    "Carrot": (),
    "Cauliflower": (),
    "Cluster beans": ("guar",),
    "Colocasia": ("taro", "arbi"),
    "Cowpea": ("lobia", "black-eyed pea"),
    "Cucumber": ("kheera",),
    "Drumstick": ("moringa", "sahjan"),
    "Fenugreek": ("methi",),
    "Garlic": ("lahsun",),
    "Green chilli": ("green chili", "chilli", "chili"),
    "Ivy gourd": ("tindora", "kundru"),
    "Lablab bean": ("hyacinth bean", "field bean", "sem"),
    "Okra": ("bhindi", "ladyfinger"),
    "Onion": ("spring onion", "scallion", "pyaz"),
    "Pea": ("peas", "garden pea", "sugar snap pea"),
    "Pointed gourd": ("parwal", "parval"),
    "Potato": ("aloo",),
    "Pumpkin": ("kaddu",),
    "Radish": ("mooli",),
    "Ridge gourd": ("turai", "torai"),
    "Snake gourd": ("padwal",),
    "Spinach": ("palak",),
    "Sponge gourd": ("gilki", "nenua"),
    "Sweet corn": ("maize", "corn"),
    "Sweet potato": ("shakarkand",),
    "Tapioca": ("cassava",),
    "Tinda": ("apple gourd", "round gourd"),
    "Tomato": (),
    "Winged bean": (),
    "Yam": ("elephant foot yam", "suran", "jimikand"),
    "Zucchini": ("courgette",),
    "Ginger": ("adrak",),
    "Turmeric": ("haldi",),
    "Coriander": ("cilantro", "dhania"),
    "Mint": ("pudina",),
    "Mustard greens": ("sarson",),
    "Lettuce": (),
    "Mushroom": (),
}


def _normalise(value: str) -> str:
    return " ".join(
        str(value).lower().replace("_", " ").replace("-", " ").replace(",", " ").split()
    )


def vegetable_class_coverage(model_class_names):
    """Return only vegetable classes genuinely present in model metadata."""
    available = set(model_class_names)
    return {
        crop: tuple(class_name for class_name in class_names if class_name in available)
        for crop, class_names in VEGETABLE_CLASS_GROUPS.items()
        if any(class_name in available for class_name in class_names)
    }


def missing_vegetable_classes(model_class_names):
    """List configured existing-model vegetable labels absent from metadata."""
    available = set(model_class_names)
    return {
        crop: tuple(class_name for class_name in class_names if class_name not in available)
        for crop, class_names in VEGETABLE_CLASS_GROUPS.items()
        if any(class_name not in available for class_name in class_names)
    }


def vegetable_catalog():
    """Return the India-focused crop catalog as stable UI-friendly records."""
    return [
        {"crop": crop, "aliases": list(aliases)}
        for crop, aliases in INDIAN_VEGETABLE_CROPS.items()
    ]


def catalog_crop_for_class(class_name: str):
    """Map a dataset class folder such as Tomato___Early_blight to its crop."""
    crop_token = _normalise(str(class_name).split("___", 1)[0])
    for crop, aliases in INDIAN_VEGETABLE_CROPS.items():
        candidates = (crop, *aliases)
        if any(crop_token == _normalise(candidate) for candidate in candidates):
            return crop
    return None


def trained_vegetable_coverage(class_names):
    """Return crop-to-class coverage based strictly on a trained class map."""
    result = {}
    for class_name in class_names:
        crop = catalog_crop_for_class(class_name)
        if crop:
            result.setdefault(crop, []).append(class_name)
    return dict(sorted(result.items()))
