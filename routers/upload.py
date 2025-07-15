import os
from fastapi import APIRouter, UploadFile, File
from app.services.elasticsearch_service import add_file_to_elasticsearch
from app.services.file_reader import process_file

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

@router.post("/")
async def upload_file(files: list[UploadFile] = File(...)):
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(await file.read())
            content = process_file(file_path)
            full_text = " ".join(content)
            add_file_to_elasticsearch(file_path, file.filename, full_text)
    return {"message": "Arquivos processados com sucesso!"}
