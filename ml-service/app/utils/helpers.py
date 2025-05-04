import os
from typing import Optional

def ensure_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def generate_unique_filename(original_filename: str) -> str:
    base, ext = os.path.splitext(original_filename)
    return f"{base}_{uuid.uuid4().hex}{ext}"