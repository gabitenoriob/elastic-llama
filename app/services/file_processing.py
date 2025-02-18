import os
import pandas as pd
from docx import Document
import fitz  # PyMuPDF

def read_pdf(file_path):
    text = []
    doc = fitz.open(file_path)
    for page in doc:
        text.append(page.get_text())
    return text

def read_docx(file_path):
    text = []
    doc = Document(file_path)
    for para in doc.paragraphs:
        text.append(para.text)
    return text

def read_csv(file_path):
    df = pd.read_csv(file_path)
    return [' '.join(str(cell) for cell in row) for _, row in df.iterrows()]

def add_files_to_elasticsearch(files):
    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)

    for file in files:
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)

    return "Arquivos processados e adicionados ao Elasticsearch"
