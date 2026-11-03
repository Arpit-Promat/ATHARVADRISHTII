# FruitLeaf6 model artifacts

The FruitLeaf6 scanner integration uses these two files:

- `fruitleaf6_model.keras` — trained Keras model artifact, stored with Git LFS.
- `fruitleaf6_class_names.json` — the ordered 24-class list matching the model output indices.

The model includes its own MobileNetV2-style input rescaling layer and expects RGB pixel values in the `[0, 255]` range. The Streamlit scanner preserves that input range and uses the same scale when rendering the explanation overlay.

Do not reorder or manually regenerate the class-name list. If the deployed scanner reports that the model file is still a Git LFS pointer, check the Git LFS object in the repository and reboot the Streamlit app after the object is available.
