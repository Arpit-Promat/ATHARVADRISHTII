# FruitLeaf6 model artifacts

The FruitLeaf6 integration expects these two files in this directory:

- `fruitleaf6_model.keras` — trained Keras model weights.
- `fruitleaf6_class_names.json` — the exact ordered class-name list used during training (24 entries).

These files were not present in the repository when the integration was committed. Copy the original trained files into this folder before selecting FruitLeaf6 in either application. Do not generate or reorder the class names manually; their order must match the model output indices.
