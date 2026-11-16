import streamlit as st
import json
from pathlib import Path
import numpy as np
import cv2
import shap

from PIL import Image
from tensorflow.keras.models import load_model

from disease_guidance import get_disease_guidance
from decision_support import condition_family

from app_supabase_auth import current_user, session_logout
from inference_preprocessing import batch_to_uint8_rgb, preprocess_rgb_array
from prediction_engine import assess_prediction
from image_validation import load_validated_image
from streamlit_scan_history import make_session_key, save_scan
from vegetable_leaf_support import vegetable_catalog, vegetable_class_coverage


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ATHARVADRISHTI — An Intelligent and Explainable Plant Health Analysis System",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background:
            radial-gradient(circle at 85% 5%, rgba(0, 80, 70, 0.25), transparent 30%),
            radial-gradient(circle at 10% 40%, rgba(0, 55, 45, 0.18), transparent 35%),
            #020b0b;
        color: #e8fff2;
    }

    .main .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #f2fff7 !important;
    }

    p, label, .stMarkdown {
        color: #c7d9d2;
    }


    /* ---------- HEADER ---------- */

    .hero-title {
        font-size: 48px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 5px;
        color: #f5fff9;
    }

    .hero-title span {
        color: #39e56f;
    }

    .hero-subtitle {
        font-size: 18px;
        color: #d3e8df;
        margin-bottom: 18px;
    }

    .badge-row {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }

    .badge {
        padding: 8px 15px;
        border-radius: 30px;
        background: rgba(10, 75, 60, 0.45);
        border: 1px solid rgba(45, 220, 120, 0.35);
        color: #caffdf;
        font-size: 14px;
        font-weight: 600;
    }


    /* ---------- CARDS ---------- */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important;
        border: 1px solid rgba(40, 190, 110, 0.22) !important;
        background: rgba(5, 30, 27, 0.65) !important;
    }

    .section-title {
        color: #64ee83;
        font-size: 23px;
        font-weight: 750;
        margin-bottom: 4px;
    }

    .section-subtitle {
        color: #9eb8ad;
        font-size: 14px;
        margin-bottom: 15px;
    }


    /* ---------- UPLOAD ---------- */

    div[data-testid="stFileUploader"] {
        background: rgba(5, 40, 34, 0.55);
        border: 1px dashed rgba(53, 222, 113, 0.55);
        border-radius: 14px;
        padding: 8px;
    }

    div[data-testid="stFileUploader"] section {
        background: transparent !important;
    }

    div[data-testid="stFileUploaderDropzone"] {
        background: transparent !important;
    }


    /* ---------- IMAGE ---------- */

    div[data-testid="stImage"] img {
        border-radius: 12px;
    }


    /* ---------- METRIC ---------- */

    div[data-testid="stMetric"] {
        background: rgba(4, 38, 32, 0.7);
        border: 1px solid rgba(50, 200, 110, 0.22);
        border-radius: 14px;
        padding: 15px;
    }

    div[data-testid="stMetricLabel"] {
        color: #9eb8ad !important;
    }

    div[data-testid="stMetricValue"] {
        color: #55ed78 !important;
    }


    /* ---------- PROGRESS ---------- */

    div[data-testid="stProgressBar"] > div {
        background-color: rgba(70, 100, 90, 0.25);
        border-radius: 20px;
    }

    div[data-testid="stProgressBar"] > div > div {
        background: linear-gradient(
            90deg,
            #20c969,
            #61f184
        );
        border-radius: 20px;
    }


    /* ---------- SUCCESS / WARNING ---------- */

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }


    /* ---------- FOOTER ---------- */

    .footer {
        text-align: center;
        padding: 20px 0 5px 0;
        color: #718d82;
        font-size: 13px;
    }

    .footer strong {
        color: #4ee978;
    }

</style>
""", unsafe_allow_html=True)

# Keep the scanner visually consistent with the current light-green landing page.
st.markdown("""
<style>
.stApp {background:#f7faf5 !important; color:#10251a !important;}
.main .block-container {max-width:1280px !important; padding-top:2.5rem !important;}
h1,h2,h3,.hero-title {color:#10251a !important;}
p,label,.stMarkdown {color:#52675a;}
.hero-title span {color:#2fa564 !important;}
.hero-subtitle {color:#63756a !important;}
.badge {background:#edf6e8 !important;border-color:#d8e6d9 !important;color:#1d7b46 !important;}
div[data-testid="stVerticalBlockBorderWrapper"] {background:#fff !important;border:1px solid #d8e6d9 !important;}
div[data-testid="stMetric"] {background:#fff !important;border:1px solid #d8e6d9 !important;}
div[data-testid="stMetricValue"] {color:#1d7b46 !important;}
div[data-testid="stFileUploader"] {background:#f5faf2 !important;border-color:#78b98a !important;}
div[data-testid="stFileUploader"] section,div[data-testid="stFileUploaderDropzone"] {background:transparent !important;}
.section-title {color:#1d7b46 !important;}
.section-subtitle {color:#63756a !important;}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero-title">🌿 ATHARVADRISHTI</div>

<div class="hero-subtitle">
An Intelligent and Explainable Plant Health Analysis System
</div>

<div class="badge-row">
    <div class="badge">⚡ Deep Learning</div>
    <div class="badge">🔍 SHAP Explainability</div>
    <div class="badge">🌱 Plant Health Analysis</div>
</div>
""", unsafe_allow_html=True)

st.write("")

# Simple navigation is available even when this page is used as the Streamlit entry point.
nav_home, nav_dashboard, nav_logout = st.columns([1, 1, 1])
with nav_home:
    if st.button("⌂ Home", use_container_width=True, key="scanner_home"):
        st.switch_page("streamlit_app.py")
with nav_dashboard:
    if st.button("📊 My Dashboard", use_container_width=True, key="scanner_dashboard"):
        st.switch_page("pages/5_Health_Dashboard.py")
with nav_logout:
    if st.button("↪ Logout", use_container_width=True, key="scanner_logout"):
        session_logout()
        st.switch_page("streamlit_app.py")


# ============================================================
# MODEL LOADING — AUTOMATIC ROUTING (NO MANUAL MODEL SELECTOR)
# ============================================================

MODEL_OPTIONS = {
    "general": ("models/plantdoc_model.keras", "models/class_names.json"),
    "mango": ("models/mango_model.keras", "models/mango_class_names.json"),
    "fruitleaf6": ("models/FruitLeaf6/fruitleaf6_model.keras", "models/FruitLeaf6/fruitleaf6_class_names.json"),
    "wheat": ("models/wheat_model.keras", "models/wheat_class_names.json"),
    "rice_pest": ("models/rice_pest_model.keras", "models/rice_pest_class_names.json"),
}

if Path("models/vegetable_leaf_model.keras").is_file() and Path("models/vegetable_leaf_class_names.json").is_file():
    MODEL_OPTIONS["vegetable_leaf"] = (
        "models/vegetable_leaf_model.keras",
        "models/vegetable_leaf_class_names.json",
    )


@st.cache_resource
def load_ai_model(model_path, class_path):
    with open(model_path, "rb") as model_file:
        model_header = model_file.read(128)
    if model_header.startswith(b"version https://git-lfs.github.com/spec/v1"):
        raise RuntimeError(
            f"{model_path} is a Git LFS pointer, not model weights. "
            "Restore the real model artifact in the Streamlit deployment."
        )
    selected_model = load_model(model_path, compile=False)
    with open(class_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    if not isinstance(metadata, list) or not metadata or not all(isinstance(name, str) and name.strip() for name in metadata):
        raise ValueError("Class-name file must contain a non-empty JSON list.")
    output_shape = selected_model.output_shape
    if isinstance(output_shape, list) or int(output_shape[-1]) != len(metadata):
        raise ValueError(
            f"Model/class mapping mismatch for {model_path}: "
            f"output shape {output_shape}, labels {len(metadata)}."
        )
    return selected_model, metadata


def identify_plant_category(class_name):
    """Map the detected crop label into the requested Plant category hierarchy."""
    raw = str(class_name).lower()
    crop_part = raw.split("___", 1)[0] if "___" in raw else raw
    crop_part = crop_part.replace("_", " ").replace("(", " ").replace(")", " ")
    crop_part = crop_part.replace(",", " ").strip()
    first = crop_part.split()[0] if crop_part.split() else ""
    fruit = {
        "apple", "banana", "citrus", "orange", "guava", "mango", "papaya",
        "grape", "blueberry", "cherry", "raspberry", "strawberry", "peach",
        "lemon", "lime", "avocado", "pomegranate", "watermelon", "melon",
    }
    vegetables = {
        "tomato", "potato", "pepper", "squash", "eggplant", "brinjal",
        "okra", "cucumber", "cabbage", "cauliflower", "onion", "garlic",
        "carrot", "radish", "spinach", "lettuce", "bitter", "ridge", "pumpkin",
    }
    crops = {"rice", "paddy", "wheat", "corn", "maize", "soybean", "sugarcane"}
    if first in fruit:
        return "PLANT", "FRUITS"
    if first in vegetables:
        return "PLANT", "VEGETABLES"
    if first in crops or "rice" in raw or "wheat" in raw:
        return "PLANT", "CROPS"
    return "PLANT", "OTHER / UNMAPPED"


def predict_with_automatic_routing(image):
    """Evaluate available specialist models and select the strongest accepted result.

    Legacy model confidence scores are not calibrated across architectures.
    This routes only among known model outputs and is not universal plant ID.
    """
    candidates, failures = [], []
    for model_key, (model_path, class_path) in MODEL_OPTIONS.items():
        try:
            candidate_model, candidate_classes = load_ai_model(model_path, class_path)
            candidate_image = preprocess_image(image, model_key)
            raw, indices = get_predictions(candidate_image, candidate_model, candidate_classes)
            assessment = assess_prediction(raw, candidate_classes, model_key, top_k=3)
            candidates.append({
                "model_key": model_key,
                "model": candidate_model,
                "class_names": candidate_classes,
                "image_array": candidate_image,
                "predictions": raw,
                "top_indices": indices,
                "assessment": assessment,
            })
        except Exception as exc:
            failures.append(f"{model_key}: {exc}")
    if not candidates:
        raise RuntimeError("No trained classifier could be loaded. " + " | ".join(failures))
    accepted = [item for item in candidates if item["assessment"]["accepted"]]
    if not accepted:
        return None, candidates, failures
    accepted.sort(
        key=lambda item: (item["assessment"]["confidence"], item["assessment"]["margin"]),
        reverse=True,
    )
    return accepted[0], candidates, failures


# ============================================================
# CONSTANTS
# ============================================================

IMG_SIZE = 224

# Leaf / non-leaf gate.
# A stricter threshold prevents ordinary objects, food, people, documents,
# screenshots, etc. from being passed to the disease classifier.
LEAF_DETECTOR_THRESHOLD = 0.65


# ============================================================
# HELPER FUNCTIONS
# ============================================================

@st.cache_resource
def load_leaf_detector():

    detector = load_model(
        "models/leaf_detector_model.keras",
        compile=False
    )

    with open(
        "models/leaf_detector_classes.json",
        "r",
        encoding="utf-8",
    ) as f:
        detector_classes = json.load(f)

    if not isinstance(detector_classes, dict) or set(detector_classes) != {"leaf", "not_leaf"}:
        raise ValueError(
            "Leaf detector class map must contain exactly 'leaf' and 'not_leaf'."
        )
    if sorted(detector_classes.values()) != [0, 1]:
        raise ValueError(
            "Leaf detector class indices must be exactly 0 and 1."
        )
    output_shape = detector.output_shape
    if isinstance(output_shape, list) or int(output_shape[-1]) != 1:
        raise ValueError(
            f"Leaf detector must have one sigmoid output; got {output_shape}."
        )

    return detector, detector_classes


def get_leaf_probability(image_array, detector, detector_classes):

    raw_value = float(
        detector.predict(
            image_array,
            verbose=0
        )[0][0]
    )
    if not np.isfinite(raw_value) or not 0.0 <= raw_value <= 1.0:
        raise ValueError("Leaf detector returned an invalid probability.")

    leaf_index = int(
        detector_classes.get("leaf", 0)
    )

    # The binary model's sigmoid output corresponds to the class index
    # learned by flow_from_directory. Convert it to P(leaf).
    if leaf_index == 0:
        return 1.0 - raw_value

    return raw_value


def clean_class_name(name):

    name = str(name)

    name = name.replace("___", " → ")
    name = name.replace("__", " ")
    name = name.replace("_", " ")

    return name.strip()


def preprocess_image(image, model_key):

    image = image.convert("RGB")

    resized = image.resize(
        (IMG_SIZE, IMG_SIZE)
    )

    array = np.array(resized)
    return preprocess_rgb_array(array, model_key)


def get_predictions(image_array, selected_model, selected_class_names=None):

    raw_output = selected_model.predict(image_array, verbose=0)
    raw_output = np.asarray(raw_output, dtype=np.float64)

    if raw_output.ndim != 2 or raw_output.shape[0] != 1:
        raise ValueError(f"Unexpected model output shape: {raw_output.shape}")

    predictions = raw_output[0]
    if predictions.ndim != 1 or predictions.size == 0:
        raise ValueError("Model returned an empty or invalid class-probability vector.")
    if not np.all(np.isfinite(predictions)):
        raise ValueError("Model returned NaN or infinite prediction values.")

    # Softmax outputs should already be probabilities. Apply softmax only
    # when the model returns logits; never silently accept invalid values.
    looks_like_probabilities = (
        np.all(predictions >= 0)
        and np.all(predictions <= 1)
        and np.isclose(np.sum(predictions), 1.0, atol=0.05)
    )
    if not looks_like_probabilities:
        shifted = predictions - np.max(predictions)
        exp_values = np.exp(shifted)
        total = np.sum(exp_values)
        if not np.isfinite(total) or total <= 0:
            raise ValueError("Could not normalize model output.")
        predictions = exp_values / total
    else:
        predictions = predictions / np.sum(predictions)

    names = selected_class_names if selected_class_names is not None else class_names
    if predictions.size != len(names):
        raise ValueError(
            f"Prediction has {predictions.size} outputs but "
            f"{len(names)} class names are configured."
        )

    top_indices = np.argsort(predictions)[::-1][:3]
    return predictions, top_indices


# ============================================================
# SHAP EXPLANATION
# ============================================================

def generate_shap_heatmap(
    image_array,
    predicted_index,
    selected_model,
    selected_class_names,
):

    try:

        masker = shap.maskers.Image(
            "blur(32,32)",
            image_array.shape[1:]
        )

        explainer = shap.Explainer(
            selected_model,
            masker,
            output_names=selected_class_names
        )

        shap_values = explainer(
            image_array,
            max_evals=100
        )

        values = shap_values.values

        if values.ndim == 5:

            if predicted_index < values.shape[-1]:

                heat = values[
                    0,
                    :,
                    :,
                    :,
                    predicted_index
                ]

            else:

                heat = values[0]

        elif values.ndim == 4:

            heat = values[0]

        else:

            return None

        if heat.ndim == 3:

            heat = np.mean(
                np.abs(heat),
                axis=-1
            )

        heat = np.abs(heat)

        heat = np.nan_to_num(
            heat,
            nan=0.0,
            posinf=0.0,
            neginf=0.0
        )

        if np.max(heat) <= 0:

            return None

        heat = (
            heat /
            np.max(heat)
        )

        heat = (
            heat * 255
        ).astype(np.uint8)

        heat = cv2.resize(
            heat,
            (IMG_SIZE, IMG_SIZE)
        )

        heat = cv2.GaussianBlur(
            heat,
            (0, 0),
            5
        )

        color_heatmap = cv2.applyColorMap(
            heat,
            cv2.COLORMAP_JET
        )

        color_heatmap = cv2.cvtColor(
            color_heatmap,
            cv2.COLOR_BGR2RGB
        )

        # Reconstruct the RGB image using the same model-specific input scale.
        # Raw-pixel models must not be multiplied by 255 a second time.
        original = batch_to_uint8_rgb(image_array, selected_model_key)

        alpha = (
            heat.astype(np.float32) /
            255.0
        )

        alpha = (
            alpha[..., None] *
            0.65
        )

        result = (
            original * (1 - alpha)
            +
            color_heatmap * alpha
        )

        result = np.clip(
            result,
            0,
            255
        ).astype(np.uint8)

        return result

    except Exception:

        return None


# Heuristic colour/edge overlays are intentionally not presented as model explanations.


# ============================================================
# UPLOAD SECTION
# ============================================================

st.markdown(
    '<div class="section-title">🔬 Analyze Your Plant Leaf</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Upload a clear leaf image and let ATHARVADRISHTI identify the most likely plant condition and explain the visual regions that influenced the prediction.'
    '</div>',
    unsafe_allow_html=True
)

if "camera_open" not in st.session_state:
    st.session_state["camera_open"] = False

upload_col, camera_col = st.columns(2)

with upload_col:
    uploaded_file = st.file_uploader(
        "📤 Upload Leaf Image",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp",
        ],
        help="Upload a clear JPG, JPEG, PNG or WebP image of a plant leaf."
    )

with camera_col:
    if not st.session_state["camera_open"]:
        if st.button(
            "📷 Open Camera",
            use_container_width=True,
            key="open_leaf_camera"
        ):
            st.session_state["camera_open"] = True
            st.rerun()
    else:
        if st.button(
            "✕ Close Camera",
            use_container_width=True,
            key="close_leaf_camera"
        ):
            st.session_state["camera_open"] = False
            st.rerun()

camera_file = None

# The camera widget is created only after the user clicks Open Camera.
if st.session_state["camera_open"]:
    camera_file = st.camera_input(
        "📷 Capture Leaf",
        key="leaf_camera",
        help="Capture a clear image of the plant leaf.",
        resolution="720p",
    )

# Use the camera image when available; otherwise use the uploaded file.
input_file = camera_file if camera_file is not None else uploaded_file


# ============================================================
# NO IMAGE
# ============================================================

if input_file is None:

    with st.container(border=True):

        st.info(
            "👆 Upload a leaf image or click **📷 Open Camera** to capture one."
        )

        st.markdown("### 💡 For better results")

        tips_col1, tips_col2, tips_col3 = st.columns(3)

        with tips_col1:
            st.write("🌿 **Clear leaf**")
            st.caption("Use a sharp and visible leaf image.")

        with tips_col2:
            st.write("💡 **Good lighting**")
            st.caption("Avoid extremely dark photographs.")

        with tips_col3:
            st.write("🎯 **Good framing**")
            st.caption("Keep the leaf clearly visible.")

    st.stop()


# ============================================================
# IMAGE PREVIEW + SUBMIT
# ============================================================

st.markdown("### 🖼️ Ready to Analyze")

preview_col, submit_col = st.columns([1.4, 0.6])

with preview_col:
    try:
        preview_image = load_validated_image(input_file.getvalue(), input_file.name)
        st.image(
            preview_image,
            caption="Preview — press Analyze when you are ready.",
            width="stretch"
        )
    except Exception as image_error:
        st.error(f"❌ Could not use this image: {image_error}")
        st.stop()

with submit_col:
    st.markdown("#### 🚀 Submit")
    st.caption("The AI will not start until you press the button below.")
    analyze_requested = st.button(
        "🧠 Analyze Image",
        use_container_width=True,
        type="primary",
        key="analyze_leaf_image",
    )

if not analyze_requested:
    st.info(
        "✅ Image selected. Press **🧠 Analyze Image** to start leaf validation and disease analysis."
    )
    st.stop()


# ============================================================
# LOAD IMAGE
# ============================================================

original_image = preview_image.copy()


# ============================================================
# PREPROCESS
# ============================================================

# ============================================================
# LEAF VALIDATION + AUTOMATIC MODEL ROUTING
# ============================================================

leaf_probability = None
try:
    detector_input = preprocess_image(original_image, "general")
    leaf_detector, leaf_detector_classes = load_leaf_detector()
    leaf_probability = get_leaf_probability(
        detector_input, leaf_detector, leaf_detector_classes
    )
    if leaf_probability < LEAF_DETECTOR_THRESHOLD:
        st.error("🚫 No clear plant leaf was detected in this image.")
        st.warning(
            f"Leaf detector confidence: {leaf_probability * 100:.2f}%. "
            "Upload a clear, close-up leaf image."
        )
        st.stop()
    st.success(f"✅ Leaf detected — confidence {leaf_probability * 100:.2f}%")
except Exception as detector_error:
    st.warning(
        "Leaf validation could not run. Continuing with available plant classifiers; "
        "results may be less reliable."
    )
    st.caption(str(detector_error))


# ============================================================
# AUTOMATIC CATEGORY + SPECIALIST MODEL SELECTION
# ============================================================

with st.spinner("🧠 Detecting plant category and selecting the best available specialist..."):
    selected_candidate, evaluated_candidates, model_failures = predict_with_automatic_routing(
        original_image
    )

if selected_candidate is None:
    st.error("⚠️ No available model produced a sufficiently reliable prediction.")
    if evaluated_candidates:
        best_candidate = max(
            evaluated_candidates,
            key=lambda item: item["assessment"]["confidence"],
        )
        best_assessment = best_candidate["assessment"]
        st.write(
            f"Best unconfirmed candidate: **{clean_class_name(best_assessment['prediction'])}** "
            f"({best_assessment['confidence']:.2f}%)"
        )
    st.info(
        "No diagnosis has been issued. Some model artifacts may be missing or "
        "unavailable in this deployment."
    )
    with st.expander("Model availability details"):
        for failure in model_failures:
            st.write("• " + failure)
    st.stop()

model = selected_candidate["model"]
class_names = selected_candidate["class_names"]
image_array = selected_candidate["image_array"]
predictions = selected_candidate["predictions"]
top_indices = selected_candidate["top_indices"]
assessment = selected_candidate["assessment"]
selected_model_key = selected_candidate["model_key"]

predicted_index = int(assessment["predicted_index"])
predicted_name = clean_class_name(assessment["prediction"])
confidence = float(assessment["confidence"])
prediction_margin = float(assessment["margin"])

main_category, plant_category = identify_plant_category(assessment["prediction"])
st.markdown(
    f"**Detected category:** {main_category} → {plant_category}  ·  "
    f"**Automatically selected model:** {selected_model_key}"
)

# Save accepted and rejected outcomes with an explicit status. A rejected
# candidate is never stored as a completed diagnosis.
try:
    authenticated_user = current_user()
    if authenticated_user:
        scan_session_key = make_session_key(
            input_file.getvalue(),
            input_file.name,
            predicted_name,
        )
        if st.session_state.get("last_history_scan_key") != scan_session_key:
            save_scan(
                user_id=str(authenticated_user["id"]),
                session_key=scan_session_key,
                filename=input_file.name,
                prediction=predicted_name if assessment["accepted"] else None,
                confidence=round(confidence, 2),
                status=assessment["status"],
                top_predictions=[
                    {
                        "rank": rank,
                        "prediction": clean_class_name(class_names[int(index)]),
                        "confidence": round(float(predictions[int(index)]) * 100, 2),
                    }
                    for rank, index in enumerate(top_indices, start=1)
                ],
            )
            st.session_state["last_history_scan_key"] = scan_session_key
except Exception:
    st.warning(
        "The analysis ran, but this scan could not be saved to your history. "
        "Check the Supabase scan_history table and its Row Level Security policies."
    )

if not assessment["accepted"]:
    st.error("⚠️ The model could not make a sufficiently reliable prediction.")
    st.write(f"Best candidate: **{predicted_name}**")
    st.write(f"Confidence: **{confidence:.2f}%** (minimum 60%)")
    st.write(f"Top-two margin: **{prediction_margin:.2f} percentage points** (minimum 20)")
    st.info(
        "No disease diagnosis has been issued. Try a sharper, well-lit close-up "
        "of one leaf, or consult an agricultural expert if symptoms persist."
    )
    with st.expander("View candidate scores"):
        for item in assessment["top_predictions"]:
            st.write(
                f"{item['rank']}. {clean_class_name(item['class_name'])} — "
                f"{item['confidence']:.2f}%"
            )
    st.stop()


# ============================================================
# IMAGE INFORMATION
# ============================================================

st.write("")

info_col1, info_col2 = st.columns(
    [1.05, 0.95]
)


with info_col1:

    with st.container(border=True):

        st.markdown(
            "### 🌿 Uploaded Leaf"
        )

        st.image(
            original_image,
            width="stretch"
        )


with info_col2:

    with st.container(border=True):

        st.markdown(
            "### 📋 Image Information"
        )

        width, height = original_image.size

        info_data = {
            "File Name": input_file.name,
            "Original Size": f"{width} × {height} px",
            "Model Input Size": "224 × 224 px",
            "Image Type": "RGB Leaf Image",
            "Leaf Detector": (f"{leaf_probability * 100:.2f}% leaf" if leaf_probability is not None else "Not applied — fruit/leaf model"),
            "Analysis": "Plant Health Analysis"
        }

        for key, value in info_data.items():

            left, right = st.columns(
                [1, 1.35]
            )

            with left:
                st.caption(key)

            with right:
                st.write(value)


# ============================================================
# DIAGNOSIS + TOP 3
# ============================================================

st.write("")

diagnosis_col, prediction_col = st.columns(
    [1, 1.15]
)


# ============================================================
# AI DIAGNOSIS
# ============================================================

with diagnosis_col:

    with st.container(border=True):

        st.markdown(
            "### 🧠 AI Diagnosis"
        )

        st.caption(
            "MOST LIKELY CONDITION"
        )

        st.markdown(
            f"## 🌱 {predicted_name}"
        )

        st.markdown(
            f"# {confidence:.2f}%"
        )

        st.caption(
            "Model Confidence Score"
        )

        st.progress(
            min(
                max(confidence / 100, 0.0),
                1.0
            )
        )


# ============================================================
# TOP 3
# ============================================================

with prediction_col:

    with st.container(border=True):

        st.markdown(
            "### 🏆 Top 3 Predictions"
        )

        for rank, index in enumerate(
            top_indices,
            start=1
        ):

            index = int(index)

            name = clean_class_name(
                class_names[index]
            )

            score = (
                float(
                    predictions[index]
                ) * 100
            )

            rank_col, name_col, score_col = st.columns(
                [0.5, 3.5, 1]
            )

            with rank_col:

                st.markdown(
                    f"### {rank}"
                )

            with name_col:

                st.write(
                    f"**{name}**"
                )

                st.progress(
                    min(
                        max(score / 100, 0.0),
                        1.0
                    )
                )

            with score_col:

                st.write(
                    f"**{score:.2f}%**"
                )


# ============================================================
# PLANT HEALTH INFORMATION — OCCURRENCE + PREVENTION
# ============================================================

guidance = get_disease_guidance(predicted_name)
healthy_result = "healthy" in predicted_name.lower()
family = condition_family(predicted_name)

FAMILY_CONTEXT = {
    "healthy-leaf classification": (
        "No disease pattern was classified from this image.",
        "No disease spread pathway is implied by a healthy prediction.",
        "Continue normal monitoring because a single image cannot represent the whole plant."
    ),
    "fungal-like leaf disease pattern": (
        "Usually associated with fungal pathogens that colonize susceptible plant tissue.",
        "Depending on the condition, spores can spread through wind, rain splash, wet foliage or infected plant residue.",
        "Humidity, prolonged leaf wetness, dense canopies and infected debris can increase disease pressure."
    ),
    "rust-like fungal pattern": (
        "Usually associated with rust fungi that produce spores on susceptible plant tissue.",
        "Spores can move by wind and, for some rusts, infection depends on moisture and alternate host plants.",
        "Cool/wet periods, leaf wetness and susceptible new growth can favor infection."
    ),
    "leaf-spot pattern": (
        "Often associated with pathogens that produce localized spots or lesions on leaf tissue.",
        "Spread may occur through rain splash, irrigation water, wind-driven moisture or contact with infected material.",
        "Wet foliage, humidity and poor airflow can increase the chance of new spots developing."
    ),
    "bacterial-spot-like pattern": (
        "Usually associated with bacterial infection of leaf or fruit tissue.",
        "Bacteria can spread through rain splash, contaminated plant material, wounds, seed or handling.",
        "Warm, humid weather and repeated leaf wetness can favor bacterial spread."
    ),
    "viral-pattern classification": (
        "Associated with a plant virus affecting leaf development and function.",
        "Spread depends on the virus and may involve insect vectors, infected planting material or mechanical plant-to-plant contact.",
        "Vector pressure, infected plants and repeated contact can increase transmission risk."
    ),
    "mite-related visual pattern": (
        "Associated with feeding damage from plant-feeding mites rather than a fungal or bacterial infection.",
        "Mites can move between nearby leaves and plants and may build up rapidly under favorable weather conditions.",
        "Hot, dry conditions and plant water stress can favor mite population growth."
    ),
    "rot / fungal-like lesion pattern": (
        "Often associated with fungi or other pathogens that colonize damaged or susceptible plant tissue.",
        "Inoculum can persist in infected tissue or residue and spread through moisture, spores or plant-to-plant contact.",
        "Wet conditions, damaged tissue and poor sanitation can increase risk."
    ),
    "blight-like leaf pattern": (
        "Usually associated with pathogens that can expand rapidly across susceptible leaf tissue.",
        "Spread may occur through spores or infected water/residue, depending on the specific disease.",
        "Prolonged moisture, suitable temperature and dense foliage can accelerate spread."
    ),
    "visual plant-condition classification": (
        "The model detected a visual plant-condition pattern, but the current label does not have a specific causal profile.",
        "The exact spread pathway depends on the confirmed cause.",
        "Use repeated observations and crop-specific expert guidance to identify the underlying problem."
    ),
}

occurrence_context = FAMILY_CONTEXT.get(
    family,
    FAMILY_CONTEXT["visual plant-condition classification"]
)

st.write("")

st.markdown(
    '<div class="section-title">🌱 Plant Health Information — How it occurs & How to prevent it</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'A concise explanation of the AI result, common occurrence pathway and practical prevention steps. '
    'This is educational decision support, not a confirmed biological diagnosis or treatment prescription.'
    '</div>',
    unsafe_allow_html=True
)

info_col1, info_col2 = st.columns(2)

with info_col1:
    with st.container(border=True):
        if healthy_result:
            st.markdown("### ✅ What does this result mean?")
            st.write(
                "The AI classified the uploaded leaf as **healthy**. "
                "No disease-related pattern was strong enough to become the top prediction for this image."
            )
            st.markdown("### 🔎 What should you do?")
            st.markdown("✅ Continue routine monitoring of new and older leaves.")
            st.markdown("✅ Maintain good sanitation, airflow and appropriate irrigation.")
            st.markdown("✅ Re-scan if you notice spots, discoloration, curling or other changes.")
        else:
            st.markdown("### 🔬 How does it occur?")
            st.write(guidance["how_it_occurs"])
            st.markdown("### 🌦️ What can favor its spread?")
            st.write(occurrence_context[2])
            st.markdown("### 🧭 Common spread pathway")
            st.write(occurrence_context[1])

with info_col2:
    with st.container(border=True):
        st.markdown("### 🛡️ Prevention")
        for step in guidance["prevention"]:
            st.markdown(f"✅ {step}")

        if not healthy_result:
            st.markdown("### 🧪 Common cause / pattern")
            st.write(occurrence_context[0])

if guidance.get("note"):
    st.info(f"ℹ️ {guidance['note']}")

# ============================================================
# EXPLAINABLE AI
# ============================================================

st.write("")

st.markdown(
    '<div class="section-title">🔎 Explainable AI — Why did the model predict this?</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'SHAP highlights the image regions that contributed most strongly to the model prediction.'
    '</div>',
    unsafe_allow_html=True
)


with st.spinner(
    "🔎 Generating AI explanation..."
):

    shap_image = generate_shap_heatmap(
        image_array,
        predicted_index,
        model,
        class_names,
    )


if shap_image is None:
    st.info(
        "SHAP could not generate an explanation for this image/model. "
        "No colour- or edge-based substitute is shown because it would not "
        "represent the model's actual reasoning."
    )
else:
    with st.container(border=True):
        st.markdown("### 🔥 SHAP model explanation")
        st.caption(
            "This attribution map estimates which image regions influenced the selected model output."
        )
        st.image(shap_image, use_container_width=True)
    st.warning(
        "SHAP is a model-attribution method, not a verified disease boundary or measurement of infection severity."
    )


# ============================================================
# AI EXPLANATION + MAP GUIDE
# ============================================================

st.write("")

explain_col, guide_col = st.columns(
    [1.35, 0.9]
)


with explain_col:

    with st.container(border=True):

        st.markdown(
            "### 💡 AI Explanation"
        )

        explanation_points = [

            (
                "Prediction",
                f"The model identified **{predicted_name}** as the most likely class."
            ),

            (
                "Model confidence",
                f"The model assigned approximately **{confidence:.2f}%** confidence to this prediction."
            ),

            (
                "Important regions",
                (
                    "The SHAP attribution map estimates influential image regions."
                    if shap_image is not None
                    else "No model-attribution map was available for this prediction."
                )
            ),

            (
                "Leaf colour",
                "Colour differences such as yellow, brown or unusually dark regions can contribute to plant disease classification."
            ),

            (
                "Leaf texture",
                "Spots, patches, surface patterns and texture changes may provide useful visual information to the model."
            ),

            (
                "Spatial pattern",
                "The model also considers where visual patterns appear across different regions of the leaf."
            ),

            (
                "Interpretation",
                "The highlighted regions should be treated as model-important areas rather than an exact biological disease boundary."
            )

        ]

        for number, (
            title,
            explanation
        ) in enumerate(
            explanation_points,
            start=1
        ):

            st.markdown(
                f"**🟢 {number}. {title}**"
            )

            st.write(
                explanation
            )


with guide_col:

    with st.container(border=True):

        st.markdown("### 🎨 How to Read the SHAP Map")
        if shap_image is not None:
            st.markdown("🔴 **Red / yellow**")
            st.caption("Stronger positive or negative attribution magnitude in this visualization; interpretation depends on the SHAP output and colour scale.")
            st.divider()
            st.markdown("🔵 **Blue**")
            st.caption("Lower displayed attribution magnitude. Colours are not disease severity.")
        else:
            st.info("A colour legend is unavailable because no SHAP map was generated.")


    with st.container(border=True):

        st.markdown(
            "### ⚠️ Important"
        )

        st.info(
            (
                "The SHAP map estimates which image regions influenced the selected model output; "
                "it is not a verified disease boundary."
            )
            if shap_image is not None
            else "No SHAP attribution map was available for this image, so no highlighted region is being claimed."
        )


# ============================================================
# HEALTH STATUS
# ============================================================

st.write("")

if "healthy" in predicted_name.lower():

    st.success(
        "🌿 The model's top prediction indicates a healthy leaf."
    )

else:

    st.warning(
        "⚠️ The model detected a disease-related visual pattern."
    )


# ============================================================
# DISCLAIMER
# ============================================================

with st.expander(
    "ℹ️ Important Information"
):

    st.write(
        """
        ATHARVADRISHTI provides an AI-based visual classification
        of plant leaf images.

        The highlighted regions show areas that influenced
        the model's visual decision.

        They should NOT be considered an exact measurement
        of disease severity or the exact infected area.

        For real agricultural treatment decisions,
        consult an agriculture expert.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        🌿 <strong>ATHARVADRISHTI</strong><br>
        Intelligent Plant Health Analysis • Deep Learning • SHAP Explainable AI<br>
        Major Project • CSE / AI & ML 💚
    </div>
    """,
    unsafe_allow_html=True
)
