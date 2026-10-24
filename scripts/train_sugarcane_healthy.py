"""Train a one-class anomaly detector using healthy sugarcane leaf images only.

This does NOT train a disease-name classifier. It learns the appearance of healthy
leaves; images with unusually high reconstruction error can be flagged for review.
Run from the repository root:
    python scripts/train_sugarcane_healthy.py
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import tensorflow as tf

ROOT = Path(__file__).resolve().parents[1]
IMAGE_SIZE = (160, 160)
BATCH_SIZE = 8
EPOCHS = 20
SEED = 42
EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def find_images(folder: Path) -> list[Path]:
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder}")
    return sorted(p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSIONS)


def load_dataset(paths: list[str], training: bool = False) -> tf.data.Dataset:
    ds = tf.data.Dataset.from_tensor_slices(paths)

    def load(path):
        image = tf.io.read_file(path)
        image = tf.io.decode_image(image, channels=3, expand_animations=False)
        image.set_shape([None, None, 3])
        image = tf.image.resize(image, IMAGE_SIZE)
        image = tf.cast(image, tf.float32) / 255.0
        return image, image

    ds = ds.map(load, num_parallel_calls=tf.data.AUTOTUNE)
    if training:
        ds = ds.shuffle(min(len(paths), 1000), seed=SEED, reshuffle_each_iteration=True)
    return ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)


def build_autoencoder() -> tf.keras.Model:
    inputs = tf.keras.Input(shape=(*IMAGE_SIZE, 3), name="healthy_leaf")
    x = tf.keras.layers.Conv2D(16, 3, strides=2, padding="same", activation="relu")(inputs)
    x = tf.keras.layers.Conv2D(32, 3, strides=2, padding="same", activation="relu")(x)
    x = tf.keras.layers.Conv2D(64, 3, strides=2, padding="same", activation="relu")(x)
    x = tf.keras.layers.Conv2D(96, 3, strides=2, padding="same", activation="relu")(x)
    x = tf.keras.layers.Conv2DTranspose(64, 3, strides=2, padding="same", activation="relu")(x)
    x = tf.keras.layers.Conv2DTranspose(32, 3, strides=2, padding="same", activation="relu")(x)
    x = tf.keras.layers.Conv2DTranspose(16, 3, strides=2, padding="same", activation="relu")(x)
    outputs = tf.keras.layers.Conv2DTranspose(
        3, 3, strides=2, padding="same", activation="sigmoid", name="reconstructed_leaf"
    )(x)
    model = tf.keras.Model(inputs, outputs, name="sugarcane_healthy_autoencoder")
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="mse")
    return model


def main() -> None:
    tf.keras.utils.set_random_seed(SEED)
    raw = input(
        r'Enter the healthy sugarcane images folder (e.g. C:\Users\Dell\Downloads\Healthy Leaves): '
    ).strip().strip('"')
    folder = Path(raw).expanduser()
    paths = [str(p) for p in find_images(folder)]
    if len(paths) < 10:
        raise ValueError(f"Only {len(paths)} images found. Please choose the folder containing the images.")

    random.Random(SEED).shuffle(paths)
    val_count = max(1, int(round(len(paths) * 0.2)))
    val_paths, train_paths = paths[:val_count], paths[val_count:]
    print(f"Healthy sugarcane images found: {len(paths)}")
    print(f"Training images: {len(train_paths)} | Validation images: {len(val_paths)}")
    print("Training a one-class anomaly detector; disease names will NOT be predicted.")

    model = build_autoencoder()
    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.3, patience=2, min_lr=1e-6),
    ]
    model.fit(
        load_dataset(train_paths, training=True),
        validation_data=load_dataset(val_paths),
        epochs=EPOCHS,
        callbacks=callbacks,
        verbose=1,
    )

    # Use healthy validation reconstruction errors to create a review threshold.
    errors = []
    for batch_x, _ in load_dataset(val_paths):
        reconstructed = model(batch_x, training=False)
        per_image = tf.reduce_mean(tf.square(batch_x - reconstructed), axis=[1, 2, 3])
        errors.extend(float(v) for v in per_image.numpy())
    threshold = float(np.mean(errors) + 3 * np.std(errors))

    models_dir = ROOT / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / "sugarcane_healthy_autoencoder.keras"
    metadata_path = models_dir / "sugarcane_healthy_threshold.json"
    model.save(model_path)
    metadata_path.write_text(
        json.dumps({
            "purpose": "one-class healthy sugarcane leaf anomaly screening",
            "image_size": list(IMAGE_SIZE),
            "reconstruction_error_threshold": threshold,
            "threshold_method": "mean + 3 standard deviations of healthy validation reconstruction MSE",
            "training_images": len(train_paths),
            "validation_images": len(val_paths),
            "warning": "This model does not name or diagnose diseases. High error means review the image; it is not a medical/agronomic diagnosis."
        }, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\nSaved model: {model_path}")
    print(f"Saved threshold metadata: {metadata_path}")
    print(f"Healthy validation reconstruction-error threshold: {threshold:.6f}")
    print("Note: this model flags unusual images for review; it does not identify a disease class.")


if __name__ == "__main__":
    main()
