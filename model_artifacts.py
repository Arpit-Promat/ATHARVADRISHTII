"""Small deployment preflight checks for model artifacts."""
from __future__ import annotations

from pathlib import Path

GIT_LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec/v1"


def ensure_model_artifact(path: str | Path) -> Path:
    """Fail early for missing files or unresolved Git LFS pointer stubs."""
    artifact = Path(path)
    if not artifact.is_file():
        raise FileNotFoundError(
            f"Required model artifact is missing: {artifact}. "
            "Check the repository path and Streamlit Cloud deployment files."
        )
    with artifact.open("rb") as model_file:
        header = model_file.read(128)
    if header.startswith(GIT_LFS_POINTER_PREFIX):
        raise RuntimeError(
            f"{artifact} is a Git LFS pointer, not the model binary. "
            "Confirm Git LFS download is enabled and the artifact is available."
        )
    if not header:
        raise RuntimeError(f"Model artifact is empty: {artifact}.")
    return artifact
