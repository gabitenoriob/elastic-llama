from flask import Flask, request, jsonify, render_template
import os
import pandas as pd
from docx import Document
import fitz  # PyMuPDF
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import torch  # Para verificar e utilizar a GPU
from transformers import AutoModel, AutoTokenizer
from elasticsearch import Elasticsearch

# Configuração do Elasticsearch
es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

# Função para criar o índice dinamicamente
def create_elasticsearch_index(index_name='report_data'):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body={
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1
            },
            "mappings": {
                "properties": {
                    "content": {"type": "text"},
                    "filename": {"type": "text"}
                }
            }
        })
        print(f"Índice '{index_name}' criado com sucesso.")
    else:
        print(f"Índice '{index_name}' já existe.")

# Verificação da disponibilidade da GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Usando dispositivo: {device}")

# Função para verificar a GPU e exibir informações detalhadas
def check_gpu_status():
    if torch.cuda.is_available():
        print("CUDA está disponível!")
        print("Dispositivo ativo:", torch.cuda.current_device())
        print("Nome do dispositivo:", torch.cuda.get_device_name(torch.cuda.current_device()))
        print("Memória total:", torch.cuda.get_device_properties(torch.cuda.current_device()).total_memory)
        print("Memória utilizada:", torch.cuda.memory_allocated(torch.cuda.current_device()))
        print("Memória livre:", torch.cuda.memory_reserved(torch.cuda.current_device()))
    else:
        print("CUDA não está disponível.")

# Chamada para verificar o status da GPU
check_gpu_status()

# Caminho para o diretório onde você salvou o modelo
model_name = "C:\\Users\\brunowto\\multi-qa-MiniLM-L6-cos-v1"

# Configurando o modelo e tokenizer para usar o dispositivo
model = AutoModel.from_pretrained(model_name).to(device)  # Envia para o dispositivo
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Configuração das embeddings com o dispositivo correto
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs={"device": device.type}  # Passa o dispositivo explicitamente
)

# Configuração do servidor LM Studio (LLM)
base_url = "http://localhost:1234"
completions_endpoint = f"{base_url}/v1/completions"


# Configuração do text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
    is_separator_regex=False
)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Pasta para armazenar uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def add_files_to_elasticsearch():
    directory = app.config['UPLOAD_FOLDER']
    print("Iniciando o processo de adição ao Elasticsearch...")

    # Função para processar arquivos
    def process_file(file_path):
        print(f"Processando arquivo: {file_path}")
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
        print(f"Arquivo ignorado: {file_path} (tipo não suportado)")
        return []

    # Processar arquivos na pasta
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            file_content = process_file(file_path)
            if file_content:
                doc_content = " ".join(file_content)
                # Indexar documento no Elasticsearch
                try:
                    es.index(
                        index="report_data",
                        body={"content": doc_content, "filename": file_name}
                    )
                    print(f"Arquivo '{file_name}' adicionado ao Elasticsearch.")
                except Exception as e:
                    print(f"Erro ao adicionar '{file_name}' ao Elasticsearch: {e}")
    print("Processo de adição ao Elasticsearch finalizado.")


def search_documents(query, index_name='report_data'):
    search_query = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["content"]
            }
        }
    }
    try:
        response = es.search(index=index_name, body=search_query)
        print(f"Documentos encontrados: {len(response['hits']['hits'])}")
        return response['hits']['hits']
    except Exception as e:
        print(f"Erro ao buscar documentos: {e}")
        return []


def get_llm_response(prompt):
    payload = {
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.0,
        "top_p": 0.8
    }
    
    response = requests.post(completions_endpoint, json=payload)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["text"].strip()
    else:
        return f"Erro: {response.status_code} - {response.text}"


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return jsonify({"message": "Requisição POST recebida na raiz."})
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist("files")
    allowed_extensions = {'.pdf', '.xlsx', '.xls', '.docx', '.csv'}  # Adicione outras extensões que você deseja permitir

    for file in files:
        if file:
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in allowed_extensions:
                print(f"Arquivo ignorado: {file.filename} (tipo não suportado)")
                continue
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)
            print(f"Arquivo salvo: {file.filename}")

    # Adiciona arquivos ao Elasticsearch
    create_elasticsearch_index()
    add_files_to_elasticsearch()
    
    return jsonify({"message": "Arquivos carregados com sucesso!"})


@app.route('/ask', methods=['POST'])
def ask():
    question = request.json['question']
    results = search_documents(question)

    if results:
        documents = [hit['_source']['content'] for hit in results]
        combined_text = " ".join(documents[:2])  # Combina textos dos dois primeiros documentos

        prompt = f"""
Você tem um conjunto de documentos contendo informações sobre diversos temas. Responda à seguinte pergunta de forma clara e detalhada com base nas informações fornecidas.

Texto dos documentos:
{combined_text}

Pergunta:
{question}

Resposta:
"""
        llm_response = get_llm_response(prompt)
        return jsonify({"response": llm_response})
    else:
        return jsonify({"response": "Nenhum documento relevante encontrado."})


def read_pdf(file_path):
    text = []
    try:
        doc = fitz.open(file_path)
        for page in doc:
            page_text = page.get_text()
            if page_text.strip():
                text.append(page_text)
    except Exception as e:
        print(f"Erro ao processar PDF: {file_path}, Erro: {str(e)}")
    return text

def read_excel(file_path):
    text = []
    try:
        chunk_size = 10000
        for chunk in pd.read_excel(file_path, chunksize=chunk_size):
            for _, row in chunk.iterrows():
                text.append(' '.join(str(cell) for cell in row))
    except Exception as e:
        print(f"Erro ao processar Excel: {file_path}, Erro: {str(e)}")
    return text

def read_xls(file_path):
    text = []
    try:
        book = xlrd.open_workbook(file_path)
        for sheet in book.sheets():
            for row_idx in range(sheet.nrows):
                row = sheet.row(row_idx)
                text.append(' '.join(str(cell.value) for cell in row))
    except Exception as e:
        print(f"Erro ao processar XLS: {file_path}, Erro: {str(e)}")
    return text

def read_docx(file_path):
    text = []
    try:
        doc = Document(file_path)
        for para in doc.paragraphs:
            if para.text.strip():
                text.append(para.text)
    except Exception as e:
        print(f"Erro ao processar DOCX: {file_path}, Erro: {str(e)}")
    return text

def read_csv(file_path):
    text = []
    try:
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            text.append(' '.join(str(cell) for cell in row))
    except Exception as e:
        print(f"Erro ao processar CSV: {file_path}, Erro: {str(e)}")
    return text

if __name__ == '__main__':
    app.run(debug=True)
