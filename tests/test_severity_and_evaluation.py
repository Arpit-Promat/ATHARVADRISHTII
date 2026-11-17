import unittest

from severity_engine import assess_observed_severity, build_safe_action_guidance
from evaluate_real_world import evaluate
import tempfile
from pathlib import Path


class SeverityEngineTests(unittest.TestCase):
    def test_observations_not_confidence_define_band(self):
        result = assess_observed_severity("few_leaves", "one_plant", "minor_growth_change")
        self.assertEqual(result["basis"], "manual_field_observations")
        self.assertFalse(result["score_is_percentage"])
        self.assertNotIn("confidence", result)

    def test_high_concern_adds_prompt_review(self):
        result = assess_observed_severity("many_leaves_or_multiple_plants", "multiple_rows_or_area", "wilting_or_major_functional_decline")
        actions = build_safe_action_guidance("Tomato___Early_blight", result)["actions"]
        self.assertEqual(result["priority"], "urgent_review")
        self.assertIn("Arrange prompt in-person crop assessment, especially if plants are wilting or decline is spreading.", actions[0])

    def test_invalid_observation_rejected(self):
        with self.assertRaises(ValueError):
            assess_observed_severity("severe", "one_plant", "no_obvious_impact")

    def test_no_chemical_prescription(self):
        guidance = build_safe_action_guidance("Tomato___Early_blight")
        self.assertIsNone(guidance["chemical_prescription"])
        self.assertTrue(guidance["requires_local_confirmation_before_treatment"])


class EvaluationTests(unittest.TestCase):
    def test_reports_rejection_and_per_crop(self):
        csv_text = "image_id,true_label,predicted_label,crop,split,confidence,accepted\n1,A,A,tomato,test,0.9,true\n2,B,A,tomato,test,0.8,true\n3,B,,potato,test,0.2,false\n"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "predictions.csv"
            path.write_text(csv_text, encoding="utf-8")
            report = evaluate(str(path))
        self.assertEqual(report["overall"]["images"], 3)
        self.assertEqual(report["overall"]["rejected"], 1)
        self.assertIn("tomato", report["per_crop"])
        self.assertIn("potato", report["per_crop"])


if __name__ == "__main__":
    unittest.main()
