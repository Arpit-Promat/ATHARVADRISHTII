"""Train the dedicated India vegetable-leaf classifier.

Expected folders:
dataset/VegetableLeaves/train/<Crop>___<condition>/*.jpg
dataset/VegetableLeaves/val/<Crop>___<condition>/*.jpg

Examples: Tomato___healthy, Tomato___Early_blight, Brinjal___healthy,
Brinjal___Phomopsis_blight. Class names must describe real labels in the data.
The default mode requires all catalog crops and at least two labelled classes
per crop. Use --allow-partial only for a clearly labelled pilot model.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from vegetable_leaf_support import INDIAN_VEGETABLE_CROPS, catalog_crop_for_class

ROOT = Path(__file__).resolve().parent
TRAIN_DIR = ROOT / "dataset" / "VegetableLeaves" / "train"
VAL_DIR = ROOT / "dataset" / "VegetableLeaves" / "val"
MODEL_PATH = ROOT / "models" / "vegetable_leaf_model.keras"
CLASS_PATH = ROOT / "models" / "vegetable_leaf_class_names.json"
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16


def validate_dataset(train_data, val_data, allow_partial: bool) -> None:
    train_classes = train_data.class_indices
    val_classes = val_data.class_indices
    if train_classes != val_classes:
        raise SystemExit(
            "Training/validation class folders or indices do not match. "
            "Create the same class folders in train and val."
        )
    if len(train_classes) < 2:
        raise SystemExit("At least two labelled classes are required.")

    crop_to_classes = {}
    unknown = []
    for label in train_classes:
        crop = catalog_crop_for_class(label)
        if crop is None:
            unknown.append(label)
        else:
            crop_to_classes.setdefault(crop, []).append(label)

    if unknown:
        raise SystemExit(
            "Unknown crop prefixes in class folders: " + ", ".join(unknown)
            + ". Use canonical crop names from vegetable_leaf_support.py."
        )

    one_label_crops = [crop for crop, labels in crop_to_classes.items() if len(labels) < 2]
    if one_label_crops:
        raise SystemExit(
            "Disease classification needs at least two real labelled classes "
            "per crop (for example healthy + a disease). Missing for: "
            + ", ".join(sorted(one_label_crops))
        )

    missing = sorted(set(INDIAN_VEGETABLE_CROPS) - set(crop_to_classes))
    if missing and not allow_partial:
        raise SystemExit(
            f"Dataset covers {len(crop_to_classes)}/{len(INDIAN_VEGETABLE_CROPS)} "
            "catalog crops. Add labelled leaf classes for: " + ", ".join(missing)
            + ". For a pilot model only, rerun with --allow-partial."
        )

    print(f"Vegetable crops represented: {len(crop_to_classes)}/{len(INDIAN_VEGETABLE_CROPS)}")
    print(f"Training classes: {len(train_classes)}")
    if missing:
        print("PILOT MODEL — not full India catalog coverage. Missing:", ", ".join(missing))
    else:
        print("Full catalog crop coverage found in dataset folders.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-partial", action="store_true",
                        help="Train a pilot model on the supplied crop subset.")
    parser.add_argument("--epochs", type=int, default=15)
    args = parser.parse_args()

    if args.epochs < 1:
        raise SystemExit("--epochs must be at least 1.")
    if not TRAIN_DIR.is_dir() or not VAL_DIR.is_dir():
        raise SystemExit(
            "Vegetable dataset folders not found. See VEGETABLE_LEAF_TRAINING.md."
        )

    train_gen = ImageDataGenerator(
        rescale=1.0 / 255.0,
        rotation_range=20,
        width_shift_range=0.12,
        height_shift_range=0.12,
        zoom_range=0.15,
        horizontal_flip=True,
        brightness_range=(0.85, 1.15),
    )
    val_gen = ImageDataGenerator(rescale=1.0 / 255.0)

    train_data = train_gen.flow_from_directory(
        str(TRAIN_DIR), target_size=IMAGE_SIZE, batch_size=BATCH_SIZE,
        class_mode="categorical", shuffle=True, seed=42,
    )
    val_data = val_gen.flow_from_directory(
        str(VAL_DIR), target_size=IMAGE_SIZE, batch_size=BATCH_SIZE,
        class_mode="categorical", shuffle=False,
    )
    validate_dataset(train_data, val_data, args.allow_partial)

    class_names = [
        name for name, index in sorted(
            train_data.class_indices.items(), key=lambda item: item[1]
        )
    ]

    base = MobileNetV2(
        weights="imagenet", include_top=False,
        input_shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3),
    )
    base.trainable = False
    x = GlobalAveragePooling2D()(base.output)
    x = Dropout(0.35)(x)
    output = Dense(len(class_names), activation="softmax")(x)
    model = Model(inputs=base.input, outputs=output)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    callbacks = [
        EarlyStopping(
            monitor="val_loss", patience=4, restore_best_weights=True,
        ),
        ModelCheckpoint(
            str(MODEL_PATH), monitor="val_loss",
            save_best_only=True, verbose=1,
        ),
    ]
    model.fit(
        train_data, validation_data=val_data,
        epochs=args.epochs, callbacks=callbacks,
    )

    # Save class order only after the best model checkpoint has been written.
    CLASS_PATH.write_text(
        json.dumps(class_names, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print("Saved model:", MODEL_PATH)
    print("Saved ordered class labels:", CLASS_PATH)
    print("Validation metrics:", model.evaluate(val_data, verbose=0))


if __name__ == "__main__":
    main()
