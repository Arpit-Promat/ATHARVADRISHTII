import unittest

import numpy as np

from model_registry import model_identifier
from prediction_engine import assess_prediction, normalize_probabilities


class PredictionEngineTests(unittest.TestCase):
    def test_probability_vector_is_normalized(self):
        result = normalize_probabilities([2.0, 1.0, 1.0])
        self.assertAlmostEqual(float(result.sum()), 1.0, places=6)
        self.assertTrue(np.all(result >= 0))

    def test_top_prediction_and_margin(self):
        result = assess_prediction(
            [0.82, 0.10, 0.08],
            ["A", "B", "C"],
            "general",
        )
        self.assertEqual(result["prediction"], "A")
        self.assertEqual(result["predicted_index"], 0)
        self.assertEqual(result["confidence"], 82.0)
        self.assertEqual(result["margin"], 72.0)
        self.assertTrue(result["accepted"])
        self.assertEqual(len(result["top_predictions"]), 3)

    def test_low_confidence_is_rejected(self):
        result = assess_prediction(
            [0.45, 0.35, 0.20],
            ["A", "B", "C"],
            "general",
        )
        self.assertFalse(result["accepted"])
        self.assertEqual(result["status"], "rejected")

    def test_registry_identifiers_are_stable(self):
        self.assertEqual(model_identifier("general"), "general@1.0.0")
        self.assertEqual(model_identifier("mango"), "mango@1.0.0")
        self.assertEqual(model_identifier("leaf_detector"), "leaf_detector@1.0.0")

    def test_class_name_count_must_match_model_outputs(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            assess_prediction([0.7, 0.3], ["Only one class"], "general")

    def test_non_finite_predictions_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-finite"):
            normalize_probabilities([0.5, float("nan")])

    def test_logits_are_converted_to_probabilities(self):
        result = normalize_probabilities([2.0, 1.0, 0.0])
        self.assertAlmostEqual(float(result.sum()), 1.0, places=6)
        self.assertGreater(float(result[0]), float(result[1]))


if __name__ == "__main__":
    unittest.main()
