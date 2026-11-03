import json
from pathlib import Path

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# =========================
# DATASET PATH
# =========================
TRAIN_DIR = Path("dataset/PlantVillage/train")
VAL_DIR = Path("dataset/PlantVillage/val")

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

print("Checking dataset...")

if not TRAIN_DIR.exists():
    raise SystemExit(f"ERROR: Training folder not found: {TRAIN_DIR}")

if not VAL_DIR.exists():
    raise SystemExit(f"ERROR: Validation folder not found: {VAL_DIR}")

print("Training folder:", TRAIN_DIR)
print("Validation folder:", VAL_DIR)

# =========================
# DATA AUGMENTATION
# =========================
train_datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    rotation_range=20,
    width_shift_range=0.15,
    height_shift_range=0.15,
    zoom_range=0.15,
    horizontal_flip=True
)

val_datagen = ImageDataGenerator(
    rescale=1.0 / 255
)

# =========================
# LOAD DATA
# =========================
train_data = train_datagen.flow_from_directory(
    str(TRAIN_DIR),
    target_size=(224, 224),
    batch_size=8,
    class_mode="categorical",
    shuffle=True
)

val_data = val_datagen.flow_from_directory(
    str(VAL_DIR),
    target_size=(224, 224),
    batch_size=8,
    class_mode="categorical",
    shuffle=False
)

print("\n==============================")
print("DATASET LOADED")
print("==============================")
print("Training images:", train_data.samples)
print("Validation images:", val_data.samples)
print("Number of classes:", train_data.num_classes)
print("==============================\n")

# Keep the exact class-index order for this training run.
class_names = [
    name
    for name, index in sorted(
        train_data.class_indices.items(),
        key=lambda x: x[1]
    )
]
if train_data.class_indices != val_data.class_indices:
    raise SystemExit(
        "ERROR: Training and validation class-index mappings differ. "
        "Use matching class folders before training."
    )

# =========================
# MOBILENETV2
# =========================
print("Loading MobileNetV2...")

base_model = MobileNetV2(
    weights="imagenet",
    include_top=False,
    input_shape=(224, 224, 3)
)

base_model.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dropout(0.3)(x)

output = Dense(
    train_data.num_classes,
    activation="softmax"
)(x)

model = Model(
    inputs=base_model.input,
    outputs=output
)

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# =========================
# CALLBACKS
# =========================
callbacks = [
    EarlyStopping(
        monitor="val_accuracy",
        patience=2,
        restore_best_weights=True
    ),
    ModelCheckpoint(
        "models/plantdoc_model.keras",
        monitor="val_accuracy",
        save_best_only=True
    )
]

# =========================
# TRAIN
# =========================
import os
from tensorflow.keras.models import load_model

checkpoint_path = MODEL_DIR / "plantdoc_model.keras"
class_map_path = MODEL_DIR / "class_names.json"

# Resume only when a sidecar class map proves that the saved model was
# trained with exactly this class-index order. Older checkpoints without
# this metadata are retrained from the freshly built architecture.
if checkpoint_path.exists() and class_map_path.exists():
    try:
        saved_classes = json.loads(class_map_path.read_text(encoding="utf-8"))
        if saved_classes == class_names:
            previous_model = load_model(checkpoint_path, compile=False)
            if int(previous_model.output_shape[-1]) == train_data.num_classes:
                model = previous_model
                model.compile(
                    optimizer="adam",
                    loss="categorical_crossentropy",
                    metrics=["accuracy"],
                )
                print("Compatible saved model found; continuing training.")
            else:
                print("Saved model output count differs; starting a fresh model.")
        else:
            print("Saved class order differs; starting a fresh model.")
    except Exception as exc:
        print(f"Could not safely resume saved model ({exc}); starting fresh.")

print("\nStarting training...\n")

model.fit(
    train_data,
    validation_data=val_data,
    initial_epoch=0,
    epochs=5,
    callbacks=callbacks,
)

# Write the class mapping only after training completes, so it always
# describes the model that was just saved by ModelCheckpoint.
with class_map_path.open("w", encoding="utf-8") as f:
    json.dump(class_names, f, indent=2, ensure_ascii=False)

print("\n==============================")
print("TRAINING COMPLETE")
print("==============================")
print(f"Model saved in {checkpoint_path}")
print(f"Class mapping saved in {class_map_path}")