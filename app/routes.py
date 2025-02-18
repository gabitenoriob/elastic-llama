from flask import request, jsonify, render_template
from app.services.file_processing import add_files_to_elasticsearch
from app.services.llm_service import get_llm_response
from app.services.elasticsearch_service import search_documents

def init_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            return jsonify({"message": "Requisição POST recebida na raiz."})
        return render_template('index.html')

    @app.route('/upload', methods=['POST'])
    def upload_file():
        files = request.files.getlist("files")
        message = add_files_to_elasticsearch(files)
        return jsonify({"message": message})

    @app.route('/ask', methods=['POST'])
    def ask():
        question = request.json['question']
        results = search_documents(question)
        
        if results:
            response = get_llm_response(results, question)
            return jsonify({"response": response})
        
        return jsonify({"response": "Nenhum documento relevante encontrado."})
