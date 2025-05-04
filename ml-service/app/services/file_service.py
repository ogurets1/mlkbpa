import os
import uuid
from fastapi import UploadFile
from app.core.config import settings

async def save_upload_file(file: UploadFile) -> str:
    file_id = str(uuid.uuid4())
    file_ext = file.filename.split(".")[-1]
    file_path = f"{settings.upload_dir}/{file_id}.{file_ext}"
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    return file_path