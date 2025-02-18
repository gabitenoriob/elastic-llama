from flask import Flask
from app.services.elasticsearch_service import create_elasticsearch_index
from app.utils.gpu_checker import check_gpu_status

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'uploads'

    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    create_elasticsearch_index()
    check_gpu_status()

    from app.routes import init_routes
    init_routes(app)

    return app
