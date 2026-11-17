import tempfile
import unittest
from pathlib import Path

from model_artifacts import ensure_model_artifact


class ModelArtifactPreflightTests(unittest.TestCase):
    def test_accepts_nonempty_model_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.keras"
            path.write_bytes(b"PK\\x03\\x04model-data")
            self.assertEqual(ensure_model_artifact(path), path)

    def test_rejects_missing_model_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.keras"
            with self.assertRaises(FileNotFoundError):
                ensure_model_artifact(path)

    def test_rejects_git_lfs_pointer(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.keras"
            path.write_text(
                "version https://git-lfs.github.com/spec/v1\\n"
                "oid sha256:" + "a" * 64 + "\\nsize 123\\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "Git LFS pointer"):
                ensure_model_artifact(path)

    def test_rejects_empty_model_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.keras"
            path.write_bytes(b"")
            with self.assertRaisesRegex(RuntimeError, "empty"):
                ensure_model_artifact(path)


if __name__ == "__main__":
    unittest.main()
