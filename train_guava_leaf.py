"""Train a dedicated guava-leaf classifier without changing other models.

Expected structure (same class folders in all three splits):
dataset/GuavaLeaves/{train,val,test}/Guava___<condition>/*.jpg

Use only original images in one split each. Do not mix augmented copies across
splits. Class labels must match the dataset's verified annotations.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

ROOT = Path(__file__).resolve().parent
DATA_ROOT = ROOT / "dataset" / "GuavaLeaves"
TRAIN_DIR = DATA_ROOT / "train"
VAL_DIR = DATA_ROOT / "val"
TEST_DIR = DATA_ROOT / "test"
MODEL_PATH = ROOT / "models" / "guava_leaf_model.keras"
CLASS_PATH = ROOT / "models" / "guava_leaf_class_names.json"
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16
SEED = 42


def main() -> None:
    for folder in (TRAIN_DIR, VAL_DIR, TEST_DIR):
        if not folder.is_dir():
            raise SystemExit(f"Missing dataset split: {folder}")

    train_gen = ImageDataGenerator(
        rescale=1.0 / 255.0,
        rotation_range=18,
        width_shift_range=0.12,
        height_shift_range=0.12,
        zoom_range=0.15,
        horizontal_flip=True,
        brightness_range=(0.85, 1.15),
    )
    eval_gen = ImageDataGenerator(rescale=1.0 / 255.0)

    train = train_gen.flow_from_directory(
        str(TRAIN_DIR), target_size=IMAGE_SIZE, batch_size=BATCH_SIZE,
        class_mode="categorical", shuffle=True, seed=SEED,
    )
    val = eval_gen.flow_from_directory(
        str(VAL_DIR), target_size=IMAGE_SIZE, batch_size=BATCH_SIZE,
        class_mode="categorical", shuffle=False,
    )
    test = eval_gen.flow_from_directory(
        str(TEST_DIR), target_size=IMAGE_SIZE, batch_size=BATCH_SIZE,
        class_mode="categorical", shuffle=False,
    )

    if train.class_indices != val.class_indices or train.class_indices != test.class_indices:
        raise SystemExit("Train, val and test must contain identical class folders.")
    if len(train.class_indices) < 2:
        raise SystemExit("At least two labelled guava classes are required.")
    if any(not name.startswith("Guava___") for name in train.class_indices):
        raise SystemExit("Every class folder must use the Guava___<condition> prefix.")

    class_names = [
        name for name, index in sorted(
            train.class_indices.items(), key=lambda item: item[1]
        )
    ]
    print(f"Classes: {class_names}")
    print(f"Images — train: {train.samples}, val: {val.samples}, test: {test.samples}")

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
        EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True),
        ModelCheckpoint(
            str(MODEL_PATH), monitor="val_loss",
            save_best_only=True, verbose=1,
        ),
    ]
    model.fit(
        train, validation_data=val, epochs=20, callbacks=callbacks,
    )

    # Evaluate the untouched test split only after model selection is complete.
    test_loss, test_accuracy = model.evaluate(test, verbose=0)
    probabilities = model.predict(test, verbose=0)
    predicted = np.argmax(probabilities, axis=1)
    true = test.classes
    print(f"HELD-OUT TEST loss: {test_loss:.4f}; accuracy: {test_accuracy:.4f}")
    for index, label in enumerate(class_names):
        mask = true == index
        class_accuracy = float(np.mean(predicted[mask] == index)) if np.any(mask) else float("nan")
        print(f"{label}: {int(np.sum(mask))} test images; recall={class_accuracy:.4f}")

    CLASS_PATH.write_text(
        json.dumps(class_names, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print("Saved model:", MODEL_PATH)
    print("Saved ordered class labels:", CLASS_PATH)


if __name__ == "__main__":
    main()
