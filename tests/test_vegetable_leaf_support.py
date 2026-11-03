import json
import unittest
from pathlib import Path

from vegetable_leaf_support import (
    VEGETABLE_CLASS_GROUPS,
    missing_vegetable_classes,
    vegetable_class_coverage,
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


if __name__ == "__main__":
    unittest.main()
