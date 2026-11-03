"""Model-aware image scaling helpers shared by Streamlit inference.

General and Mango classifiers were trained on RGB inputs scaled to [0, 1].
FruitLeaf6, Wheat and Rice Pest models include an internal MobileNetV2-style
Rescaling(1/127.5, offset=-1) layer and therefore expect raw RGB [0, 255].
"""
from __future__ import annotations

import numpy as np

RAW_PIXEL_MODEL_KEYS = frozenset({"fruitleaf6", "wheat", "rice_pest"})


def preprocess_rgb_array(rgb_array: np.ndarray, model_key: str) -> np.ndarray:
    """Validate an HxWx3 RGB array and return a one-image model batch."""
    image = np.asarray(rgb_array, dtype=np.float32)
    if image.ndim != 3 or image.shape[-1] != 3:
        raise ValueError(f"Expected an HxWx3 RGB image, got shape {image.shape}.")
    if image.size == 0 or not np.all(np.isfinite(image)):
        raise ValueError("Image pixels must be non-empty and finite.")
    if float(image.min()) < 0.0 or float(image.max()) > 255.0:
        raise ValueError("RGB pixel values must be in the [0, 255] range.")

    if model_key not in RAW_PIXEL_MODEL_KEYS:
        image = image / 255.0

    return np.expand_dims(image, axis=0)


def batch_to_uint8_rgb(image_batch: np.ndarray, model_key: str) -> np.ndarray:
    """Convert a preprocessed single-image batch back to displayable RGB."""
    batch = np.asarray(image_batch, dtype=np.float32)
    if batch.ndim != 4 or batch.shape[0] != 1 or batch.shape[-1] != 3:
        raise ValueError(f"Expected a single-image NHWC batch, got shape {batch.shape}.")

    image = batch[0]
    if model_key not in RAW_PIXEL_MODEL_KEYS:
        image = image * 255.0
    return np.clip(np.rint(image), 0, 255).astype(np.uint8)
