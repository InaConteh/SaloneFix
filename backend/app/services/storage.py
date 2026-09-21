import os
import hashlib
from pathlib import Path
from typing import Tuple
from app.core.config import settings


def get_storage_path() -> Path:
    storage_dir = Path(settings.STORAGE_DIR)
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir


def save_media_file(file_bytes: bytes, filename: str) -> Tuple[str, str, int]:
    """
    Save media bytes to private storage directory.
    Returns: (storage_key, sha256_hash, file_size)
    """
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    ext = os.path.splitext(filename)[1].lower()
    if not ext:
        ext = ".bin"
    storage_key = f"{sha256[:16]}_{hashlib.md5(filename.encode()).hexdigest()[:8]}{ext}"
    target_path = get_storage_path() / storage_key

    with open(target_path, "wb") as f:
        f.write(file_bytes)

    return storage_key, sha256, len(file_bytes)


def get_media_bytes(storage_key: str) -> bytes:
    """Retrieve raw media bytes from storage."""
    target_path = get_storage_path() / storage_key
    if not target_path.exists():
        raise FileNotFoundError(f"Media asset not found: {storage_key}")
    with open(target_path, "rb") as f:
        return f.read()
