"""Private, expiring access to uploaded scan media and generated explanations."""
from __future__ import annotations

import os
import re
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

TOKEN_SALT = "atharvadrishti-private-media-v1"
_SAFE_NAME = re.compile(r"^[a-zA-Z0-9_-]{1,100}\\.(?:jpg|jpeg|png|webp)$")


def private_media_dir(app_root: str) -> str:
    path = os.path.join(app_root, "instance", "private_media")
    os.makedirs(path, exist_ok=True)
    return path


def create_media_token(filename: str, secret_key: str) -> str:
    if not _SAFE_NAME.fullmatch(filename):
        raise ValueError("Invalid private media filename")
    return URLSafeTimedSerializer(secret_key, salt=TOKEN_SALT).dumps({"name": filename})


def resolve_media_token(token: str, secret_key: str, max_age: int = 1800) -> str | None:
    try:
        data = URLSafeTimedSerializer(secret_key, salt=TOKEN_SALT).loads(token, max_age=max_age)
        filename = data.get("name", "")
        return filename if isinstance(filename, str) and _SAFE_NAME.fullmatch(filename) else None
    except (BadSignature, SignatureExpired, AttributeError, TypeError):
        return None
