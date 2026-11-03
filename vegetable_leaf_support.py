"""Vegetable leaf classes already represented in the 38-class PlantDoc model.

This is a transparent coverage map, not a new classifier or newly trained model.
"""
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


def vegetable_class_coverage(model_class_names):
    """Return only supported vegetable classes, grouped by crop."""
    available = set(model_class_names)
    return {
        crop: tuple(class_name for class_name in class_names if class_name in available)
        for crop, class_names in VEGETABLE_CLASS_GROUPS.items()
    }


def missing_vegetable_classes(model_class_names):
    """List configured vegetable labels missing from the supplied model metadata."""
    available = set(model_class_names)
    return {
        crop: tuple(class_name for class_name in class_names if class_name not in available)
        for crop, class_names in VEGETABLE_CLASS_GROUPS.items()
        if any(class_name not in available for class_name in class_names)
    }
