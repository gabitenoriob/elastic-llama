from flask import Flask, request, jsonify, render_template
import os
import pandas as pd
from docx import Document
import fitz 
import requests
from elasticsearch import Elasticsearch
import xlrd

# Configuração do Elasticsearch
es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

if es.ping():
    print("Conexão bem-sucedida com Elasticsearch!")
else:
    print("Falha na conexão com Elasticsearch.")

def create_elasticsearch_index(index_name='teste'):
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

# Configuração do servidor LM Studio (LLM)
base_url = "http://127.0.0.1:1234"
completions_endpoint = f"{base_url}/v1/completions"


def get_llm_response(prompt):
    payload = {
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.0,  # Mantendo baixo para respostas mais precisas
        "top_p": 0.7,  # Reduzindo para evitar que o modelo escolha palavras redundantes
        "stop": ["\n\n", "A resposta está presente no texto:"],  # Evita loop de justificativas
        "frequency_penalty": 0.8,  # Penaliza palavras repetidas
        "presence_penalty": 0.7    # Incentiva diversidade na resposta
    }

    try:
        response = requests.post(completions_endpoint, json=payload)
        response.raise_for_status()
        text = response.json().get("choices", [{}])[0].get("text", "").strip()

        # Remover frases repetidas na resposta
        seen_sentences = set()
        filtered_text = []
        for sentence in text.split('. '):  # Divide por frases
            if sentence not in seen_sentences:
                seen_sentences.add(sentence)
                filtered_text.append(sentence)

        return '. '.join(filtered_text)

    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar ao LLM: {e}")
        return "Erro: Falha na conexão com o LLM."



def test_llm_connection():
    try:
        response = requests.post(completions_endpoint, json={
            "prompt": "Teste de conexão",
            "max_tokens": 5
        })
        response.raise_for_status()
        print("✅ Conectado ao LLM!")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar ao LLM: {e}")

test_llm_connection()

# Inicializar Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def add_file_to_elasticsearch(file_path, file_name):
    print(f"Processando arquivo: {file_name}")
    file_content = process_file(file_path)
    if file_content:
        doc_content = " ".join(file_content)
        print(f"Conteúdo extraído de {file_name}: {doc_content[:500]}...")
        try:
            es.index(
                index="teste",
                body={"content": doc_content, "filename": file_name}
            )
            print(f"Arquivo '{file_name}' adicionado ao Elasticsearch.")
        except Exception as e:
            print(f"Erro ao adicionar '{file_name}' ao Elasticsearch: {e}")
    else:
        print(f"Nenhum conteúdo extraído de {file_name}")

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
        return open(file_path, 'r').readlines()
    else:
        print(f"Arquivo ignorado: {file_path} (tipo não suportado)")
    return []

def search_documents(keywords, index_name='teste'):
    create_elasticsearch_index(index_name)

    
    query = {
        "query": {
            "bool": {
                "should": [
                    {"match_phrase": {"content": " ".join(keywords)}},  # Busca com as palavras-chave extraídas
                    {"match": {"content": {"query": " ".join(keywords), "fuzziness": "AUTO"}}},  # Busca com erros de digitação
                    {"wildcard": {"content": f"*{' '.join(keywords)}*"}}  # Busca com wildcard (*)
                ],
                "minimum_should_match": 1
            }
        }
    }

    print(f"🔍 Consulta ES: {query}")  # Debug

    try:
        response = es.search(index=index_name, body=query)
        print(f"📄 Documentos encontrados: {len(response['hits']['hits'])}")
        return response['hits']['hits']
    except Exception as e:
        print(f"❌ Erro ao buscar documentos: {e}")
        return []


@app.route('/reset', methods=['POST'])
def reset_uploads():
    try:
        es.indices.delete(index="teste", ignore=[400, 404])  # Deleta o índice
        create_elasticsearch_index()  # Recria o índice
        print("Uploads antigos excluídos com sucesso!")
        return jsonify({"message": "Uploads antigos excluídos, pronto para novos uploads!"})
    except Exception as e:
        print(f"Erro ao excluir uploads: {e}")
        return jsonify({"message": "Erro ao excluir uploads."}), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist("files")
    for file in files:
        if file:
            file_path = os.path.normpath(os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(file.filename)))
            if not os.path.exists(file_path): 
                file.save(file_path)
                print(f"Arquivo salvo: {file.filename}")
                add_file_to_elasticsearch(file_path, file.filename)
            else:
                print(f"Arquivo '{file.filename}' já existe, ignorando upload.")
    return jsonify({"message": "Processamento concluído!"})

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     file = request.files.get("file")  # Mudando para um único arquivo
#     if file:
#         file_path = os.path.normpath(os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(file.filename)))
#         if not os.path.exists(file_path):  # Verifica se o arquivo já existe
#             file.save(file_path)
#             print(f"Arquivo salvo: {file.filename}")
#             add_file_to_elasticsearch(file_path, file.filename)
#         else:
#             print(f"Arquivo '{file.filename}' já existe, ignorando upload.")
#         return jsonify({"message": "Processamento concluído!"})
#     else:
#         return jsonify({"message": "Nenhum arquivo enviado."})

import spacy

# Carregar o modelo de linguagem em português do spaCy
nlp = spacy.load("pt_core_news_sm")

def extract_keywords(question):
    # Usar spaCy para analisar a pergunta
    doc = nlp(question)

    # Filtrar as palavras-chave (substantivos, verbos, e adjetivos)
    keywords = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
    
    return keywords

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json['question']
    keywords = extract_keywords(question)
    results = search_documents(keywords)
    if results:
        documents = [hit['_source']['content'] for hit in results]
        combined_text = " ".join(documents[:2])
        print(f"Texto combinado para LLM: {combined_text[:500]}...")
        prompt = f"Com base no seguinte texto, responda à pergunta de forma concisa e sem repetições. Se a resposta não estiver clara, indique isso.\n\nTexto: {combined_text}\n\nPergunta: {question}\n\nResposta:"
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