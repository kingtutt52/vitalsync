"""
File storage service.

Currently writes to the local filesystem under STORAGE_ROOT/{user_id}/{file_type}/.
Swap this module's implementation for an S3 client to migrate to cloud storage —
the interface (save_file, delete_file) stays the same.
"""
import os
import shutil
from pathlib import Path

from fastapi import UploadFile

from app.core.config import get_settings

settings = get_settings()


def _user_dir(user_id: str, file_type: str) -> Path:
    p = Path(settings.storage_root) / user_id / file_type
    p.mkdir(parents=True, exist_ok=True)
    return p


async def save_file(user_id: str, file_type: str, upload: UploadFile) -> str:
    """
    Persist the uploaded file to disk and return its absolute path.
    The filename is kept as-is; callers should ensure no path-traversal characters.
    """
    safe_name = Path(upload.filename).name  # strip directory components
    dest = _user_dir(user_id, file_type) / safe_name

    # Append a counter if the file already exists, rather than silently overwriting
    counter = 1
    stem = dest.stem
    suffix = dest.suffix
    while dest.exists():
        dest = dest.with_name(f"{stem}_{counter}{suffix}")
        counter += 1

    with open(dest, "wb") as f:
        shutil.copyfileobj(upload.file, f)

    return str(dest)


def delete_file(path: str) -> None:
    """Remove a file from storage. Silently ignores missing files."""
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
