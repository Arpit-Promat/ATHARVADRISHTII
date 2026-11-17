"""Evaluate held-out labelled predictions without ML-library dependencies.

CSV required columns: image_id,true_label,predicted_label,crop,split,confidence,accepted
Use one row per independently sampled image. Keep all images from the same plant,
plot, or source group in only one split before creating this CSV.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


def _safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def _metrics(rows: list[dict[str, str]]) -> dict:
    labels = sorted({r["true_label"] for r in rows} | {r["predicted_label"] for r in rows if r["accepted"] == "true"})
    result = {}
    f1_values = []
    for label in labels:
        tp = sum(r["accepted"] == "true" and r["predicted_label"] == label and r["true_label"] == label for r in rows)
        fp = sum(r["accepted"] == "true" and r["predicted_label"] == label and r["true_label"] != label for r in rows)
        fn = sum(r["true_label"] == label and not (r["accepted"] == "true" and r["predicted_label"] == label) for r in rows)
        precision = _safe_div(tp, tp + fp)
        recall = _safe_div(tp, tp + fn)
        f1 = _safe_div(2 * precision * recall, precision + recall)
        result[label] = {"support": sum(r["true_label"] == label for r in rows), "precision": precision, "recall": recall, "f1": f1}
        f1_values.append(f1)
    accepted = [r for r in rows if r["accepted"] == "true"]
    correct = sum(r["predicted_label"] == r["true_label"] for r in accepted)
    total = len(rows)
    confusion = {
        actual: {
            predicted: sum(
                r["true_label"] == actual
                and r["accepted"] == "true"
                and r["predicted_label"] == predicted
                for r in rows
            )
            for predicted in labels
        }
        for actual in labels
    }
    weighted_f1 = _safe_div(
        sum(item["f1"] * item["support"] for item in result.values()),
        sum(item["support"] for item in result.values()),
    )
    return {
        "images": total,
        "accepted": len(accepted),
        "rejected": total - len(accepted),
        "coverage": _safe_div(len(accepted), total),
        "selective_accuracy": _safe_div(correct, len(accepted)),
        "end_to_end_correct_rate": _safe_div(correct, total),
        "macro_f1_including_rejected_as_misses": _safe_div(sum(f1_values), len(f1_values)),
        "weighted_f1_including_rejected_as_misses": weighted_f1,
        "confusion_matrix_accepted_predictions": confusion,
        "confusion_matrix_labels": labels,
        "per_class": result,
    }


def evaluate(path: str, split: str = "test") -> dict:
    with open(path, newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    required = {"image_id", "true_label", "predicted_label", "crop", "split", "confidence", "accepted"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"CSV must contain rows and columns: {', '.join(sorted(required))}")
    selected = [r for r in rows if r["split"].strip().lower() == split.lower()]
    if not selected:
        raise ValueError(f"No rows found for split={split!r}")
    seen_ids = set()
    for row in selected:
        for field in ("image_id", "true_label", "crop"):
            if not row[field].strip():
                raise ValueError(f"{field} must not be empty")
        image_id = row["image_id"].strip()
        if image_id in seen_ids:
            raise ValueError(f"Duplicate image_id in selected split: {image_id!r}")
        seen_ids.add(image_id)
        if row["accepted"].strip().lower() not in {"true", "false"}:
            raise ValueError("accepted must be true or false")
        row["accepted"] = row["accepted"].strip().lower()
        row["predicted_label"] = row["predicted_label"].strip()
        if row["accepted"] == "true" and not row["predicted_label"]:
            raise ValueError("predicted_label must not be empty for accepted predictions")
        try:
            confidence = float(row["confidence"])
        except (TypeError, ValueError):
            raise ValueError("confidence must be numeric from 0 to 1")
        if not math.isfinite(confidence) or not 0 <= confidence <= 1:
            raise ValueError("confidence must be finite and between 0 and 1")
    by_crop = defaultdict(list)
    for row in selected:
        by_crop[row["crop"]].append(row)
    return {
        "split": split,
        "overall": _metrics(selected),
        "per_crop": {crop: _metrics(group) for crop, group in sorted(by_crop.items())},
        "calibration_note": "Confidence values are reported as supplied; calibration metrics are intentionally omitted until model-specific calibration is validated.",
        "data_quality_warnings": [
            "This report is meaningful only for a genuinely held-out, correctly labelled, representative dataset.",
            "Group-split by plant/plot/source to prevent near-duplicate leakage.",
            "A crop/class absent from the CSV cannot be evaluated; do not infer its accuracy.",
            "Do not treat classifier confidence as disease severity.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path")
    parser.add_argument("--split", default="test")
    parser.add_argument("--output", default="evaluation_report.json")
    args = parser.parse_args()
    report = evaluate(args.csv_path, args.split)
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["overall"], indent=2))
    print(f"Full report written to {args.output}")


if __name__ == "__main__":
    main()
