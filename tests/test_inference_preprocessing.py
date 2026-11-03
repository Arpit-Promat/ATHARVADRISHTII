import unittest

import numpy as np

from inference_preprocessing import batch_to_uint8_rgb, preprocess_rgb_array


class InferencePreprocessingTests(unittest.TestCase):
    def setUp(self):
        self.rgb = np.array(
            [[[0, 64, 255], [10, 128, 200]], [[20, 180, 240], [255, 1, 90]]],
            dtype=np.uint8,
        )

    def test_general_and_mango_are_scaled_to_zero_one(self):
        for key in ("general", "mango"):
            with self.subTest(model=key):
                batch = preprocess_rgb_array(self.rgb, key)
                self.assertEqual(batch.shape, (1, 2, 2, 3))
                self.assertAlmostEqual(float(batch.max()), 1.0)
                self.assertAlmostEqual(float(batch.min()), 0.0)

    def test_mobilenet_rescaling_models_keep_raw_pixels(self):
        for key in ("fruitleaf6", "wheat", "rice_pest"):
            with self.subTest(model=key):
                batch = preprocess_rgb_array(self.rgb, key)
                self.assertEqual(batch.shape, (1, 2, 2, 3))
                self.assertAlmostEqual(float(batch.max()), 255.0)

    def test_display_conversion_round_trips_all_preprocessing_modes(self):
        for key in ("general", "mango", "fruitleaf6", "wheat", "rice_pest"):
            with self.subTest(model=key):
                batch = preprocess_rgb_array(self.rgb, key)
                restored = batch_to_uint8_rgb(batch, key)
                np.testing.assert_array_equal(restored, self.rgb)

    def test_rejects_non_rgb_input(self):
        with self.assertRaises(ValueError):
            preprocess_rgb_array(np.zeros((4, 4), dtype=np.uint8), "general")


if __name__ == "__main__":
    unittest.main()
