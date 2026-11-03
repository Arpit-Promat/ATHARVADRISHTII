"""Train a separate MobileNetV2 classifier for plant species or plant diseases.

Expected folders:
  DATA/train/<class_name>/
  DATA/val/<class_name>/
  DATA/test/<class_name>/

This script does not alter the existing ATHARVADRISHTI models.
"""
import argparse
import json
from pathlib import Path

import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=("plant", "disease"), required=True)
    parser.add_argument("--data", required=True, help="Dataset root with train/val/test folders")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--image-size", type=int, default=224)
    args = parser.parse_args()

    root = Path(args.data)
    for split in ("train", "val", "test"):
        if not (root / split).is_dir():
            raise SystemExit(f"Missing folder: {root / split}")

    train_ds = tf.keras.utils.image_dataset_from_directory(
        root / "train", image_size=(args.image_size, args.image_size),
        batch_size=args.batch_size, label_mode="int", shuffle=True, seed=42
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        root / "val", image_size=(args.image_size, args.image_size),
        batch_size=args.batch_size, label_mode="int", shuffle=False
    )
    test_ds = tf.keras.utils.image_dataset_from_directory(
        root / "test", image_size=(args.image_size, args.image_size),
        batch_size=args.batch_size, label_mode="int", shuffle=False
    )

    class_names = train_ds.class_names
    if len(class_names) < 2:
        raise SystemExit("At least two class folders are required.")
    if class_names != val_ds.class_names or class_names != test_ds.class_names:
        raise SystemExit("Train/val/test class folders must match exactly.")

    autotune = tf.data.AUTOTUNE
    def prepare(images, labels):
        return preprocess_input(tf.cast(images, tf.float32)), labels

    train_ds = train_ds.map(prepare, num_parallel_calls=autotune).prefetch(autotune)
    val_ds = val_ds.map(prepare, num_parallel_calls=autotune).prefetch(autotune)
    test_ds = test_ds.map(prepare, num_parallel_calls=autotune).prefetch(autotune)

    base = MobileNetV2(
        weights="imagenet", include_top=False,
        input_shape=(args.image_size, args.image_size, 3)
    )
    base.trainable = False

    inputs = layers.Input(shape=(args.image_size, args.image_size, 3))
    x = base(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(len(class_names), activation="softmax")(x)
    model = Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    out = Path("models")
    out.mkdir(exist_ok=True)
    model_path = out / f"global_{args.task}_model.keras"
    class_path = out / f"global_{args.task}_class_names.json"

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=3, restore_best_weights=True
        ),
        tf.keras.callbacks.ModelCheckpoint(
            model_path, monitor="val_accuracy", save_best_only=True
        )
    ]
    model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=callbacks)
    loss, accuracy = model.evaluate(test_ds, verbose=1)
    model.save(model_path)
    class_path.write_text(json.dumps(class_names, indent=2), encoding="utf-8")
    print(f"Task: {args.task}")
    print(f"Classes: {len(class_names)}")
    print(f"Test accuracy: {accuracy:.4f}")
    print(f"Saved model: {model_path}")
    print(f"Saved classes: {class_path}")
    print("Note: test accuracy is meaningful only if the test split is independent and representative.")


if __name__ == "__main__":
    main()
