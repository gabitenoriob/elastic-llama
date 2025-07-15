from fastapi import APIRouter
from app.services.elasticsearch_service import create_elasticsearch_index, es

router = APIRouter()

@router.post("/")
def reset_uploads():
    try:
        es.indices.delete(index="teste", ignore=[400, 404])
        create_elasticsearch_index()
        return {"message": "Índice resetado. Pronto para novos uploads!"}
    except Exception as e:
        print(f"Erro ao resetar: {e}")
        return {"message": "Erro ao resetar uploads."}
