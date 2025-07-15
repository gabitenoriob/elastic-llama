from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, ask, reset
from services.elasticsearch_service import create_elasticsearch_index

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(ask.router, prefix="/ask", tags=["Perguntas"])
app.include_router(reset.router, prefix="/reset", tags=["Reset"])

@app.on_event("startup")
def startup_event():
    create_elasticsearch_index()
    print("API iniciada e Elasticsearch indexado!")
