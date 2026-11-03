import json
import unittest
from pathlib import Path

from vegetable_leaf_support import (
    VEGETABLE_CLASS_GROUPS,
    INDIAN_VEGETABLE_CROPS,
    catalog_crop_for_class,
    missing_vegetable_classes,
    vegetable_class_coverage,
    trained_vegetable_coverage,
)


class VegetableLeafCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with Path("models/class_names.json").open(encoding="utf-8") as handle:
            cls.class_names = json.load(handle)

    def test_plantdoc_general_model_contains_configured_vegetables(self):
        coverage = vegetable_class_coverage(self.class_names)
        self.assertEqual(set(coverage), {"Tomato", "Potato", "Bell Pepper", "Squash"})
        self.assertEqual(sum(map(len, coverage.values())), 16)
        self.assertEqual(missing_vegetable_classes(self.class_names), {})

    def test_each_vegetable_group_has_at_least_one_class(self):
        coverage = vegetable_class_coverage(self.class_names)
        for crop, class_names in coverage.items():
            with self.subTest(crop=crop):
                self.assertTrue(class_names)

    def test_missing_labels_are_reported_not_silently_invented(self):
        missing = missing_vegetable_classes(["Tomato___healthy"])
        self.assertEqual(set(missing), set(VEGETABLE_CLASS_GROUPS))
        self.assertEqual(len(missing["Tomato"]), 9)

    def test_india_catalog_includes_major_and_regional_vegetables(self):
        expected = {
            "Tomato", "Brinjal", "Okra", "Potato", "Onion", "Cabbage",
            "Cauliflower", "Bottle gourd", "Bitter gourd", "Pointed gourd",
            "Spinach", "Amaranth", "Cowpea", "Cluster beans", "Tinda",
        }
        self.assertTrue(expected.issubset(set(INDIAN_VEGETABLE_CROPS)))
        self.assertGreaterEqual(len(INDIAN_VEGETABLE_CROPS), 45)

    def test_class_folder_names_map_to_canonical_crop(self):
        self.assertEqual(catalog_crop_for_class("Tomato___Early_blight"), "Tomato")
        self.assertEqual(catalog_crop_for_class("Brinjal___healthy"), "Brinjal")
        self.assertEqual(catalog_crop_for_class("Okra___Yellow_vein_mosaic"), "Okra")
        self.assertIsNone(catalog_crop_for_class("UnknownCrop___healthy"))

    def test_trained_coverage_uses_only_actual_class_names(self):
        labels = [
            "Tomato___healthy",
            "Tomato___Early_blight",
            "Brinjal___healthy",
        ]
        coverage = trained_vegetable_coverage(labels)
        self.assertEqual(coverage["Tomato"], labels[:2])
        self.assertEqual(coverage["Brinjal"], [labels[2]])
        self.assertNotIn("Okra", coverage)


if __name__ == "__main__":
    unittest.main()
