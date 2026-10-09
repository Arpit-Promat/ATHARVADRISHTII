#!/usr/bin/env python3
"""Import/audit a locally downloaded ATHARVADRISHTI fruit-and-leaf dataset.

This script never uploads images to GitHub and never deletes/renames originals.
It inventories extracted images, infers labels conservatively from folder names,
and writes a CSV for review before any model training.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
from collections import Counter
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
OUT_DIR = ROOT / "data" / "metadata"

# Crops already represented by the current 38-class general model or Mango model.
EXISTING_CROPS = {
    "apple", "citrus", "orange", "mango", "papaya"
}
# Crops present in the six-crop fruit/leaf dataset but not in current model class lists.
NEW_CROPS = {"banana", "guava"}
CROP_ALIASES = {
    "apple": "Apple", "banana": "Banana", "citrus": "Citrus",
    "orange": "Citrus", "guava": "Guava", "mango": "Mango",
    "papaya": "Papaya",
}
PART_ALIASES = {
    "leaf": "leaf", "leaves": "leaf", "foliage": "leaf",
    "fruit": "fruit", "fruits": "fruit",
    "flower": "flower", "flowers": "flower",
    "whole plant": "whole_plant", "whole_plant": "whole_plant",
}

def normalized(text: str) -> str:
    return re.sub(r"[_-]+", " ", text).strip().lower()

def infer_crop(parts: tuple[str, ...]) -> str:
    for part in parts:
        key = normalized(part)
        for alias, canonical in CROP_ALIASES.items():
            if re.search(rf"(?<![a-z]){re.escape(alias)}(?![a-z])", key):
                return canonical
    return "UNKNOWN"

def infer_plant_part(parts: tuple[str, ...]) -> str:
    for part in parts:
        key = normalized(part)
        for alias, canonical in PART_ALIASES.items():
            if alias in key:
                return canonical
    return "unknown"

def infer_source_label(path: Path, root: Path) -> str:
    relative = path.relative_to(root)
    # Use the closest non-generic parent folder as the original class label.
    generic = {"train", "test", "valid", "validation", "images", "image", "data", "dataset"}
    for parent in relative.parents:
        if parent == Path("."):
            continue
        name = parent.name
        if normalized(name) not in generic:
            return name
    return "UNLABELED"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to the extracted dataset root")
    parser.add_argument("--dataset-id", default="mendeley_fruit_leaf_6crop")
    args = parser.parse_args()
    root = Path(args.input).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Input folder does not exist: {root}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    hashes = Counter()
    paths = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS]
    for path in paths:
        rel = path.relative_to(root)
        parts = rel.parts[:-1]
        crop = infer_crop(parts)
        plant_part = infer_plant_part(parts)
        source_label = infer_source_label(path, root)
        digest = ""
        valid = False
        width = height = ""
        note = ""
        try:
            digest = sha256(path)
            if Image is not None:
                with Image.open(path) as im:
                    im.verify()
                with Image.open(path) as im:
                    width, height = im.size
                valid = True
            else:
                note = "Pillow missing; install requirements to verify image contents."
        except Exception as exc:
            note = "unreadable: " + type(exc).__name__
        if digest:
            hashes[digest] += 1
        crop_key = crop.lower()
        rows.append({
            "image_path": str(path),
            "relative_path": str(rel),
            "dataset_id": args.dataset_id,
            "source_label": source_label,
            "crop": crop,
            "plant_part": plant_part,
            "canonical_label_candidate": f"{crop}__{plant_part}__{source_label}" if crop != "UNKNOWN" else "REVIEW_REQUIRED",
            "crop_status": "existing_crop" if crop_key in EXISTING_CROPS else ("new_crop" if crop_key in NEW_CROPS else "review_required"),
            "sha256": digest,
            "exact_duplicate": "pending",
            "valid_image": str(valid).lower(),
            "width": width,
            "height": height,
            "review_status": "needs_label_review",
            "notes": note,
        })

    for row in rows:
        row["exact_duplicate"] = str(bool(row["sha256"] and hashes[row["sha256"]] > 1)).lower()

    out = OUT_DIR / f"{args.dataset_id}_import_manifest.csv"
    fields = list(rows[0].keys()) if rows else [
        "image_path", "relative_path", "dataset_id", "source_label", "crop",
        "plant_part", "canonical_label_candidate", "crop_status", "sha256",
        "exact_duplicate", "valid_image", "width", "height", "review_status", "notes"
    ]
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Images found: {len(rows)}")
    print(f"Valid images: {sum(r['valid_image'] == 'true' for r in rows)}")
    print(f"Exact duplicate rows: {sum(r['exact_duplicate'] == 'true' for r in rows)}")
    print(f"Crop counts: {dict(Counter(r['crop'] for r in rows))}")
    print(f"Plant-part counts: {dict(Counter(r['plant_part'] for r in rows))}")
    print(f"Manifest written: {out}")
    print("Review UNKNOWN crops, plant parts, source labels, and licenses before training.")

if __name__ == "__main__":
    main()
