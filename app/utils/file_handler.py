"""
utils/file_handler.py — File upload and management utilities.
Handles secure file saving, deletion, and format conversion helpers.
"""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def save_uploaded_file(file_obj, upload_folder: str) -> tuple[str, int]:
    """
    Saves a Werkzeug FileStorage object to disk with a UUID-prefixed name.
    Returns (absolute_path, size_in_bytes).
    """
    original_name = secure_filename(file_obj.filename)
    ext = original_name.rsplit('.', 1)[-1].lower() if '.' in original_name else 'bin'
    unique_name = f"{uuid.uuid4().hex}_{original_name}"
    save_path = os.path.join(upload_folder, unique_name)

    os.makedirs(upload_folder, exist_ok=True)
    file_obj.save(save_path)

    file_size = os.path.getsize(save_path)
    return save_path, file_size


def delete_resume_file(file_path: str) -> bool:
    """Remove a resume file from disk. Returns True if deleted, False if missing."""
    if file_path and os.path.isfile(file_path):
        os.remove(file_path)
        return True
    return False


def get_extension(filename: str) -> str:
    """Return lowercase file extension without the dot."""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def human_readable_size(size_bytes: int) -> str:
    """Convert bytes to a human-readable size string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
