import pandas as pd
from docx import Document
import fitz
import xlrd

def read_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        return [page.get_text() for page in doc if page.get_text().strip()]
    except Exception as e:
        print(f"Erro PDF: {file_path} -> {e}")
        return []

def read_excel(file_path):
    try:
        return [' '.join(str(cell) for cell in row) for chunk in pd.read_excel(file_path, chunksize=10000) for _, row in chunk.iterrows()]
    except Exception as e:
        print(f"Erro Excel: {file_path} -> {e}")
        return []

def read_xls(file_path):
    try:
        book = xlrd.open_workbook(file_path)
        return [' '.join(str(cell.value) for cell in sheet.row(row_idx)) for sheet in book.sheets() for row_idx in range(sheet.nrows)]
    except Exception as e:
        print(f"Erro XLS: {file_path} -> {e}")
        return []

def read_docx(file_path):
    try:
        doc = Document(file_path)
        return [para.text for para in doc.paragraphs if para.text.strip()]
    except Exception as e:
        print(f"Erro DOCX: {file_path} -> {e}")
        return []

def read_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        return [' '.join(str(cell) for cell in row) for _, row in df.iterrows()]
    except Exception as e:
        print(f"Erro CSV: {file_path} -> {e}")
        return []

def read_txt(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.readlines()
    except Exception as e:
        print(f"Erro TXT: {file_path} -> {e}")
        return []

def process_file(file_path):
    if file_path.endswith('.pdf'):
        return read_pdf(file_path)
    elif file_path.endswith('.xlsx'):
        return read_excel(file_path)
    elif file_path.endswith('.xls'):
        return read_xls(file_path)
    elif file_path.endswith('.docx'):
        return read_docx(file_path)
    elif file_path.endswith('.csv'):
        return read_csv(file_path)
    elif file_path.endswith('.txt'):
        return read_txt(file_path)
    else:
        print(f"Tipo de arquivo não suportado: {file_path}")
        return []
