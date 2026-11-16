import io
import unittest

from PIL import Image

from image_validation import MAX_UPLOAD_BYTES, load_validated_image


def encoded_image(size=(32, 24), image_format="PNG"):
    buffer = io.BytesIO()
    Image.new("RGB", size, (30, 150, 70)).save(buffer, format=image_format)
    return buffer.getvalue()


class ImageValidationTests(unittest.TestCase):
    def test_valid_png_is_returned_as_rgb(self):
        image = load_validated_image(encoded_image(), "leaf.png")
        self.assertEqual(image.mode, "RGB")
        self.assertEqual(image.size, (32, 24))

    def test_valid_jpeg_is_accepted(self):
        image = load_validated_image(encoded_image(image_format="JPEG"), "leaf.jpg")
        self.assertEqual(image.format, "RGB")

    def test_rejects_unsupported_extension(self):
        with self.assertRaisesRegex(ValueError, "extension"):
            load_validated_image(encoded_image(), "leaf.gif")

    def test_rejects_non_image_bytes(self):
        with self.assertRaisesRegex(ValueError, "damaged|valid"):
            load_validated_image(b"not an image", "leaf.png")

    def test_rejects_empty_file(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            load_validated_image(b"", "leaf.png")

    def test_rejects_upload_over_limit(self):
        with self.assertRaisesRegex(ValueError, "10 MB"):
            load_validated_image(b"x" * (MAX_UPLOAD_BYTES + 1), "leaf.png")

    def test_rejects_excessive_pixel_dimensions(self):
        with self.assertRaisesRegex(ValueError, "dimensions"):
            load_validated_image(encoded_image((5000, 5000)), "large.png")


if __name__ == "__main__":
    unittest.main()
