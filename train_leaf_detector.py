import json
from pathlib import Path

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping

# =========================
# DATASET PATH (Leaf vs Not-Leaf)
# =========================
TRAIN_DIR = Path("dataset/LeafDetector/train")
VAL_DIR = Path("dataset/LeafDetector/val")

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
# LOAD DATA (binary classification: leaf vs not_leaf)
# =========================
train_data = train_datagen.flow_from_directory(
    str(TRAIN_DIR),
    target_size=(224, 224),
    batch_size=16,
    class_mode="binary",
    shuffle=True
)

val_data = val_datagen.flow_from_directory(
    str(VAL_DIR),
    target_size=(224, 224),
    batch_size=16,
    class_mode="binary",
    shuffle=False
)

print("\n==============================")
print("DATASET LOADED")
print("==============================")
print("Training images:", train_data.samples)
print("Validation images:", val_data.samples)
print("Class indices:", train_data.class_indices)
print("==============================\n")

if train_data.class_indices != val_data.class_indices:
    raise SystemExit("ERROR: Training and validation class-index mappings differ.")
if set(train_data.class_indices) != {"leaf", "not_leaf"}:
    raise SystemExit(f"ERROR: Expected leaf and not_leaf folders; found {sorted(train_data.class_indices)}.")

# =========================
# MOBILENETV2 (binary output)
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

# Single output neuron with sigmoid for binary classification
output = Dense(1, activation="sigmoid")(x)

model = Model(
    inputs=base_model.input,
    outputs=output
)

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

# =========================
# CALLBACKS
# =========================
callbacks = [
    EarlyStopping(
        monitor="val_accuracy",
        patience=3,
        restore_best_weights=True
    ),
]

# =========================
# TRAIN
# =========================
print("\nStarting training...\n")

history = model.fit(
    train_data,
    validation_data=val_data,
    initial_epoch=0,
    epochs=8,
    callbacks=callbacks
)

model_path = MODEL_DIR / "leaf_detector_model.keras"
class_map_path = MODEL_DIR / "leaf_detector_classes.json"
model.save(model_path)
temp_class_map_path = class_map_path.with_suffix(".json.tmp")
temp_class_map_path.write_text(json.dumps(train_data.class_indices, indent=2) + "\n", encoding="utf-8")
temp_class_map_path.replace(class_map_path)

train_acc = history.history.get("accuracy", [None])[-1]
val_acc = history.history.get("val_accuracy", [None])[-1]
if train_acc is not None and val_acc is not None:
    print(f"Final train accuracy: {train_acc:.4f}; validation accuracy: {val_acc:.4f}")
    if train_acc - val_acc > 0.15:
        print("WARNING: Large train/validation gap; possible overfitting.")

print("\n==============================")
print("TRAINING COMPLETE")
print("==============================")
print("Model saved in models/leaf_detector_model.keras")
print("Class indices saved in models/leaf_detector_classes.json")
