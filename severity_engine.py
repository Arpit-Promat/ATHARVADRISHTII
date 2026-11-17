"""Conservative field-observation severity and action guidance.

Severity is based only on user-entered field observations, never classifier
confidence, SHAP values, or image attribution. It is a triage aid, not diagnosis.
"""
from __future__ import annotations

from typing import Any

_LEVELS = {
    0: ("No visible impact reported", "routine"),
    1: ("Limited visible impact", "monitor"),
    2: ("Moderate field concern", "review"),
    3: ("High field concern", "urgent_review"),
}


def assess_observed_severity(symptom_extent: str, spread: str, plant_impact: str) -> dict[str, Any]:
    """Classify manually reported observations; each input must be a known option."""
    scales = {
        "symptom_extent": {"none": 0, "few_leaves": 1, "several_leaves": 2, "many_leaves_or_multiple_plants": 3},
        "spread": {"not_spreading_or_unknown": 0, "one_plant": 1, "nearby_plants": 2, "multiple_rows_or_area": 3},
        "plant_impact": {"no_obvious_impact": 0, "minor_growth_change": 1, "reduced_growth_or_yield_concern": 2, "wilting_or_major_functional_decline": 3},
    }
    values = {
        "symptom_extent": symptom_extent,
        "spread": spread,
        "plant_impact": plant_impact,
    }
    for key, value in values.items():
        if value not in scales[key]:
            raise ValueError(f"Unsupported {key} observation: {value!r}")

    score = sum(scales[key][value] for key, value in values.items())
    # The sum is an ordinal triage band, not a biological percentage.
    if score <= 1:
        band = 0
    elif score <= 3:
        band = 1
    elif score <= 6:
        band = 2
    else:
        band = 3
    label, priority = _LEVELS[band]
    return {
        "level": band,
        "label": label,
        "priority": priority,
        "basis": "manual_field_observations",
        "observations": values,
        "score_is_percentage": False,
        "limitations": [
            "This is a structured field-observation triage, not an AI-measured infection severity.",
            "The model confidence and SHAP map are not used in this assessment.",
            "Crop stage, cultivar, weather, laboratory confirmation and field sampling are not assessed.",
        ],
    }


def build_safe_action_guidance(predicted_label: str | None, severity: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return non-chemical IPM-first steps; no pesticide, dose, or product claims."""
    healthy = "healthy" in str(predicted_label or "").lower()
    if healthy:
        actions = [
            "Continue routine scouting of several plants and both older and newer leaves.",
            "Use clean planting material and maintain crop-appropriate irrigation and nutrition.",
            "Record new symptoms and recheck if visible changes develop.",
        ]
    else:
        actions = [
            "Photograph several affected and unaffected plants and record the date and crop growth stage.",
            "Avoid moving potentially affected plant material between plots; clean tools after handling.",
            "Remove severely damaged material only where appropriate for the crop and local practice.",
            "Review irrigation, drainage, spacing and airflow without stressing the crop.",
            "Ask a local agricultural extension officer or qualified agronomist to confirm the cause before choosing a chemical or other treatment.",
        ]
    priority = (severity or {}).get("priority")
    if priority == "urgent_review":
        actions.insert(0, "Arrange prompt in-person crop assessment, especially if plants are wilting or decline is spreading.")
    elif priority == "review":
        actions.insert(0, "Arrange crop-specific expert review soon and monitor nearby plants.")
    return {
        "actions": actions,
        "chemical_prescription": None,
        "requires_local_confirmation_before_treatment": True,
        "note": "No pesticide, dose, brand, or chemical treatment is prescribed by this tool.",
    }
