# Phase 5 + Phase 8: severity triage and real-world evaluation

## Severity and action guidance
The scanner's classifier confidence and SHAP attribution are not measurements of infection severity. `severity_engine.py` therefore accepts only three explicit field observations: symptom extent, spread, and plant impact. Its four ordinal bands are observation-based triage labels, not percentages or biological measurements. Unknown/unsupported answers are rejected.

The action guidance is integrated-pest-management-first and non-prescriptive. It does not name pesticide products, active ingredients, rates, or doses. Confirm the cause and any treatment choice with a local agricultural extension officer or qualified agronomist.

## Real-world evaluation
Run:
```bash
python evaluate_real_world.py labelled_predictions.csv --split test --output evaluation_report.json
```

Required CSV columns:
`image_id,true_label,predicted_label,crop,split,confidence,accepted`

- `confidence` is a decimal in [0,1].
- `accepted` is `true` or `false`; rejected rows still require the true label and crop.
- Use a locked test set that was not used for training, threshold tuning, or model selection.
- Split by plant, plot, farm, acquisition session, or source group before inference. Do not split near-duplicate images across train/validation/test.
- Keep the image files and any personal/farm-identifying metadata out of Git. The CSV should use non-identifying image IDs.
- Report each crop and class separately. Missing classes are not evaluated and must not be described as supported.
- This initial evaluator reports coverage, rejection, selective accuracy, end-to-end correct rate, and per-class/per-crop precision, recall and F1. It deliberately does not claim calibration; model-specific calibration requires a separate held-out calibration set and validated method.

## Current limitation
The friend's 55-crop roadmap dataset is not present in this repository. This tooling can be tested with synthetic fixtures, but no real-world accuracy claim for the 55 crops can be made until a representative labelled held-out dataset is supplied and evaluated.
