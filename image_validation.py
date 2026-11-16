"""Safe validation and decoding for user-supplied plant images."""
from __future__ import annotations

from io import BytesIO
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
_ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


def load_validated_image(file_bytes: bytes, filename: str) -> Image.Image:
    """Validate size, extension, real image format and pixel count; return RGB."""
    if not isinstance(file_bytes, (bytes, bytearray)) or not file_bytes:
        raise ValueError("The selected file is empty.")
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise ValueError("Image is too large. Please upload an image under 10 MB.")

    suffix = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in str(filename) else ""
    if suffix not in _ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported image extension. Use JPG, PNG or WebP.")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(file_bytes)) as probe:
                if probe.format not in _ALLOWED_FORMATS:
                    raise ValueError("The file content is not a supported image.")
                width, height = probe.size
                if width < 1 or height < 1 or width * height > MAX_IMAGE_PIXELS:
                    raise ValueError("Image dimensions are too large. Use an image below 20 megapixels.")
                probe.verify()

            with Image.open(BytesIO(file_bytes)) as source:
                if source.format not in _ALLOWED_FORMATS:
                    raise ValueError("The file content is not a supported image.")
                image = ImageOps.exif_transpose(source)
                image.load()
                return image.convert("RGB")
    except ValueError:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ValueError("The uploaded file is damaged or is not a valid supported image.") from exc
