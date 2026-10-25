"""Smoke-test the three locally trained crop models without modifying the app."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import tensorflow as tf

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"


def read_classes(filename: str) -> list[str]:
    path = MODELS / filename
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def test_classifier(model_file: str, classes_file: str, size: int = 224) -> None:
    model_path = MODELS / model_file
    if not model_path.exists():
        raise FileNotFoundError(f"Missing model file: {model_path}")
    classes = read_classes(classes_file)
    model = tf.keras.models.load_model(model_path, compile=False)
    # Training script expects RGB pixel values in [0, 255]; it preprocesses internally.
    sample = np.zeros((1, size, size, 3), dtype=np.float32)
    output = np.asarray(model.predict(sample, verbose=0))
    if output.ndim != 2 or output.shape[0] != 1:
        raise ValueError(f"{model_file}: unexpected output shape {output.shape}")
    if output.shape[1] != len(classes):
        raise ValueError(
            f"{model_file}: model outputs {output.shape[1]} classes but "
            f"{classes_file} contains {len(classes)} names"
        )
    print(f"PASS {model_file}: input=(1,{size},{size},3), output={output.shape}, classes={len(classes)}")
    print(f"     labels: {', '.join(classes)}")


def test_sugarcane() -> None:
    model_path = MODELS / "sugarcane_healthy_autoencoder.keras"
    metadata_path = MODELS / "sugarcane_healthy_threshold.json"
    if not model_path.exists() or not metadata_path.exists():
        raise FileNotFoundError("Sugarcane model or threshold metadata file is missing.")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    model = tf.keras.models.load_model(model_path, compile=False)
    size = int(metadata.get("image_size", [160, 160])[0])
    sample = np.zeros((1, size, size, 3), dtype=np.float32)  # autoencoder input range [0, 1]
    output = np.asarray(model.predict(sample, verbose=0))
    if output.shape != sample.shape:
        raise ValueError(f"Sugarcane autoencoder output {output.shape} does not match input {sample.shape}")
    threshold = float(metadata["reconstruction_error_threshold"])
    if not np.isfinite(threshold) or threshold < 0:
        raise ValueError("Sugarcane reconstruction threshold is invalid.")
    print(
        f"PASS {model_path.name}: input/output={output.shape}, "
        f"healthy reconstruction threshold={threshold:.6f}"
    )
    print("     This is an anomaly-screening model, not a disease classifier.")


def main() -> None:
    print("Loading and smoke-testing locally trained models...")
    test_classifier("wheat_model.keras", "wheat_class_names.json")
    test_classifier("rice_pest_model.keras", "rice_pest_class_names.json")
    test_sugarcane()
    print("\nAll three model smoke tests passed.")


if __name__ == "__main__":
    main()
