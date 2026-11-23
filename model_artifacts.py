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



def resolve_model_artifact(path: str | Path, repository: str = "Arpit-Promat/ATHARVADRISHTII") -> Path:
    """Return a real model file, downloading a public Git LFS object when needed.

    The downloaded object is cached outside the repository and verified against
    the SHA-256 OID and byte size declared by the Git LFS pointer.
    """
    import hashlib
    import json
    import os
    import re
    import tempfile

    import requests

    artifact = Path(path)
    if not artifact.is_file():
        raise FileNotFoundError(
            f"Required model artifact is missing: {artifact}. "
            "Restore the model file in the repository before running inference."
        )

    with artifact.open("rb") as model_file:
        header = model_file.read(512)

    if not header.startswith(GIT_LFS_POINTER_PREFIX):
        return ensure_model_artifact(artifact)

    pointer_text = header.decode("utf-8", errors="replace")
    oid_match = re.search(r"(?m)^oid sha256:([0-9a-f]{64})$", pointer_text)
    size_match = re.search(r"(?m)^size ([0-9]+)$", pointer_text)
    if not oid_match or not size_match:
        raise RuntimeError(f"Invalid Git LFS pointer format: {artifact}")

    expected_sha = oid_match.group(1)
    expected_size = int(size_match.group(1))
    relative_path = artifact.as_posix().lstrip("./")
    cache_root = Path(tempfile.gettempdir()) / "atharvadrishti-model-cache"
    cached = cache_root / relative_path
    cached.parent.mkdir(parents=True, exist_ok=True)

    if cached.is_file() and cached.stat().st_size == expected_size:
        digest = hashlib.sha256(cached.read_bytes()).hexdigest()
        if digest == expected_sha:
            return cached

    owner, repo_name = repository.split("/", 1)
    batch_url = f"https://github.com/{owner}/{repo_name}.git/info/lfs/objects/batch"
    response = requests.post(
        batch_url,
        headers={
            "Accept": "application/vnd.git-lfs+json",
            "Content-Type": "application/vnd.git-lfs+json",
        },
        json={
            "operation": "download",
            "transfers": ["basic"],
            "objects": [{"oid": expected_sha, "size": expected_size}],
        },
        timeout=(15, 45),
    )
    response.raise_for_status()
    payload = response.json()
    objects = payload.get("objects") or []
    if not objects or objects[0].get("error"):
        detail = objects[0].get("error", {}) if objects else {}
        raise RuntimeError(f"Git LFS download was not authorized or available for {artifact}: {detail}")

    action = (objects[0].get("actions") or {}).get("download")
    if not action or not action.get("href"):
        raise RuntimeError(f"Git LFS did not provide a download URL for {artifact}.")

    download = requests.get(
        action["href"],
        headers=action.get("header") or {},
        stream=True,
        timeout=(20, 180),
    )
    download.raise_for_status()

    temporary = cached.with_suffix(cached.suffix + ".part")
    digest = hashlib.sha256()
    total = 0
    try:
        with temporary.open("wb") as output:
            for chunk in download.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                total += len(chunk)
                if total > expected_size:
                    raise RuntimeError(f"Downloaded model exceeded its declared size: {artifact}")
                digest.update(chunk)
                output.write(chunk)
        if total != expected_size or digest.hexdigest() != expected_sha:
            raise RuntimeError(f"Downloaded model failed SHA-256/size verification: {artifact}")
        os.replace(temporary, cached)
    finally:
        if temporary.exists():
            temporary.unlink()

    return cached
