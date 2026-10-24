"""Train Wheat Disease and Rice Pest classifiers from local datasets.

This script reads the original dataset folders in place. It does not move or upload
images. Run from the repository root:
    python scripts/train_crop_models.py --model wheat
    python scripts/train_crop_models.py --model rice-pest
    python scripts/train_crop_models.py --model both

The trained .keras files and class-name JSON files are saved under models/.
"""
from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path

import numpy as np
import tensorflow as tf

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 8
SEED = 42
EPOCHS = 12
ROOT = Path(__file__).resolve().parents[1]


def image_files(folder: Path) -> list[Path]:
    return sorted(
        p for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )


def class_dirs(parent: Path) -> list[Path]:
    try:
        return sorted(p for p in parent.iterdir() if p.is_dir())
    except OSError:
        return []


def find_wheat_split(root: Path, split: str) -> tuple[Path, list[Path]] | None:
    """Find a train/test folder whose direct child folders include Wheat classes."""
    candidates = [p for p in root.rglob("*") if p.is_dir() and p.name.lower() == split]
    candidates.sort(key=lambda p: len(p.parts))
    for candidate in candidates:
        dirs = class_dirs(candidate)
        wheat_dirs = [
            d for d in dirs
            if "wheat" in d.name.lower()
            and any(word in d.name.lower() for word in ("healthy", "septoria", "stripe", "rust"))
        ]
        if len(wheat_dirs) >= 2:
            return candidate, wheat_dirs
    return None


def wheat_records(root: Path) -> tuple[list[str], list[int], list[str], list[int] | None]:
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Wheat dataset folder not found: {root}")

    train_found = find_wheat_split(root, "train")
    if not train_found:
        raise ValueError(
            "Could not find Wheat class folders under a train directory. "
            "Choose the extracted dataset root that contains Dataset/train/."
        )

    _, train_dirs = train_found
    # Keep only the three requested Wheat classes; Tomato folders are ignored.
    train_dirs = sorted(
        train_dirs,
        key=lambda p: (
            0 if "healthy" in p.name.lower() else
            1 if "septoria" in p.name.lower() else 2
        ),
    )
    names = [p.name.replace("_", " ").strip() for p in train_dirs]
    train_paths: list[str] = []
    train_labels: list[int] = []
    for label, folder in enumerate(train_dirs):
        files = image_files(folder)
        train_paths.extend(str(p) for p in files)
        train_labels.extend([label] * len(files))

    test_paths: list[str] = []
    test_labels: list[int] = []
    test_found = find_wheat_split(root, "test")
    if test_found:
        _, test_dirs = test_found
        by_normalized_name = {
            re.sub(r"[^a-z0-9]", "", p.name.lower()): p for p in test_dirs
        }
        for label, train_dir in enumerate(train_dirs):
            key = re.sub(r"[^a-z0-9]", "", train_dir.name.lower())
            test_dir = by_normalized_name.get(key)
            if test_dir:
                files = image_files(test_dir)
                test_paths.extend(str(p) for p in files)
                test_labels.extend([label] * len(files))

    if len(set(train_labels)) < 2 or not train_paths:
        raise ValueError("Not enough Wheat images/classes were found in the train folders.")
    print("\nWheat classes (Tomato classes excluded):")
    counts = Counter(train_labels)
    for i, name in enumerate(names):
        print(f"  {name}: {counts[i]} training images")
    if test_paths:
        print(f"Separate test set: {len(test_paths)} images")
    else:
        print("No matching Wheat test folders found; a validation split will be used.")
        test_labels = []
    return train_paths, train_labels, names, (test_paths, test_labels) if test_paths else None


def find_pest_root(root: Path) -> Path:
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Rice pest dataset folder not found: {root}")

    # The inspected dataset may have a wrapper folder: Downloads/Pest_V2/Pest_V2/...
    for child in class_dirs(root):
        if child.name.lower() in {"pest_v2", "pest", "rice_pest", "rice pests"}:
            if len(class_dirs(child)) >= 2:
                return child

    # If the supplied folder is a wrapper containing one actual dataset folder,
    # descend one level only when that folder has several subfolders and no images.
    children = class_dirs(root)
    if len(children) == 1 and len(class_dirs(children[0])) >= 2 and not image_files(root):
        return children[0]
    return root


def rice_pest_records(root: Path) -> tuple[list[str], list[int], list[str]]:
    dataset_root = find_pest_root(root)
    pest_dirs = class_dirs(dataset_root)
    records: list[str] = []
    labels: list[int] = []
    names: list[str] = []

    # The first folder under the dataset root is the pest name. Any nested
    # adult/egg/larva folders are pooled into that pest class intentionally.
    for pest_dir in pest_dirs:
        files = image_files(pest_dir)
        if len(files) < 2:
            print(f"Skipping {pest_dir.name}: only {len(files)} image(s), need at least 2.")
            continue
        label = len(names)
        names.append(pest_dir.name.replace("_", " ").strip())
        records.extend(str(p) for p in files)
        labels.extend([label] * len(files))

    if len(names) < 2:
        raise ValueError(
            f"Found only {len(names)} usable pest classes under {dataset_root}. "
            "Check that the supplied path points to the extracted dataset root."
        )
    print(f"\nRice pest dataset root: {dataset_root}")
    print("Nested adult/egg/larva folders are combined under each pest name.")
    counts = Counter(labels)
    for i, name in enumerate(names):
        print(f"  {name}: {counts[i]} images")
    print(f"Total usable pest images: {len(records)}")
    return records, labels, names


def split_per_class(paths: list[str], labels: list[int], validation_fraction: float = 0.2):
    rng = random.Random(SEED)
    train_p, train_y, val_p, val_y = [], [], [], []
    for label in sorted(set(labels)):
        items = [(p, y) for p, y in zip(paths, labels) if y == label]
        rng.shuffle(items)
        n_val = max(1, int(round(len(items) * validation_fraction)))
        n_val = min(n_val, len(items) - 1) if len(items) > 1 else 0
        val_items, train_items = items[:n_val], items[n_val:]
        train_p.extend(p for p, _ in train_items)
        train_y.extend(y for _, y in train_items)
        val_p.extend(p for p, _ in val_items)
        val_y.extend(y for _, y in val_items)
    return train_p, train_y, val_p, val_y


def make_dataset(paths: list[str], labels: list[int], training: bool = False):
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))

    def load_image(path, label):
        raw = tf.io.read_file(path)
        image = tf.io.decode_image(raw, channels=3, expand_animations=False)
        image.set_shape([None, None, 3])
        image = tf.image.resize(image, IMAGE_SIZE)
        image = tf.cast(image, tf.float32)
        return image, tf.cast(label, tf.int32)

    ds = ds.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
    if training:
        ds = ds.shuffle(min(len(paths), 1000), seed=SEED, reshuffle_each_iteration=True)
    return ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)


def build_model(class_count: int) -> tf.keras.Model:
    inputs = tf.keras.Input(shape=(*IMAGE_SIZE, 3), name="leaf_image")
    x = tf.keras.layers.RandomFlip("horizontal")(inputs)
    x = tf.keras.layers.RandomRotation(0.08)(x)
    x = tf.keras.layers.RandomZoom(0.10)(x)
    # Equivalent to MobileNetV2 preprocess_input for RGB pixels in [0, 255],
    # implemented as a standard layer for safer .keras serialization.
    x = tf.keras.layers.Rescaling(1.0 / 127.5, offset=-1, name="mobilenet_preprocess")(x)
    base = tf.keras.applications.MobileNetV2(
        input_shape=(*IMAGE_SIZE, 3), include_top=False, weights="imagenet"
    )
    base.trainable = False
    x = base(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.30)(x)
    outputs = tf.keras.layers.Dense(class_count, activation="softmax", name="predictions")(x)
    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def train_one(
    paths: list[str],
    labels: list[int],
    class_names: list[str],
    output_stem: str,
    explicit_test: tuple[list[str], list[int]] | None = None,
):
    if len(set(labels)) < 2:
        raise ValueError(f"{output_stem}: at least two classes are required.")

    train_p, train_y, val_p, val_y = split_per_class(paths, labels)
    if not train_p or not val_p:
        raise ValueError("Not enough images to create training and validation sets.")

    print(f"\n{output_stem}: {len(train_p)} train / {len(val_p)} validation images")
    train_ds = make_dataset(train_p, train_y, training=True)
    val_ds = make_dataset(val_p, val_y)

    counts = Counter(train_y)
    total = len(train_y)
    class_weight = {
        i: total / (len(class_names) * max(counts.get(i, 1), 1))
        for i in range(len(class_names))
    }

    model = build_model(len(class_names))
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=3, restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.3, patience=2, min_lr=1e-6
        ),
    ]
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
        class_weight=class_weight,
        callbacks=callbacks,
        verbose=1,
    )

    if explicit_test:
        test_paths, test_labels = explicit_test
        if test_paths:
            print(f"\nEvaluating on the separate test set ({len(test_paths)} images):")
            model.evaluate(make_dataset(test_paths, test_labels), verbose=1)

    models_dir = ROOT / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / f"{output_stem}_model.keras"
    classes_path = models_dir / f"{output_stem}_class_names.json"
    model.save(model_path)
    classes_path.write_text(
        json.dumps(class_names, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\nSaved model: {model_path}")
    print(f"Saved class names: {classes_path}")
    print("Keep the model and its class-name JSON file together.")


def ask_path(prompt: str) -> Path:
    raw = input(prompt).strip().strip('"')
    return Path(raw).expanduser()


def main():
    parser = argparse.ArgumentParser(description="Train ATHARVADRISHTI crop classifiers.")
    parser.add_argument(
        "--model",
        choices=("wheat", "rice-pest", "both"),
        default="both",
        help="Which classifier to train (default: both).",
    )
    args = parser.parse_args()

    tf.keras.utils.set_random_seed(SEED)
    if args.model in ("wheat", "both"):
        wheat_root = ask_path(
            r"Enter the extracted Wheat dataset root (e.g. C:\Users\Dell\Downloads\Crop Dataset): "
        )
        paths, labels, names, test_data = wheat_records(wheat_root)
        train_one(paths, labels, names, "wheat", test_data)

    if args.model in ("rice-pest", "both"):
        pest_root = ask_path(
            r"Enter the extracted Paddy/Rice pest dataset root (e.g. C:\Users\Dell\Downloads\Pest_V2): "
        )
        paths, labels, names = rice_pest_records(pest_root)
        train_one(paths, labels, names, "rice_pest")


if __name__ == "__main__":
    main()
