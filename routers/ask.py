from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.nlp_utils import extract_keywords
from app.services.elasticsearch_service import search_documents
from app.services.llm_service import get_llm_response

router = APIRouter()

class Question(BaseModel):
    question: str

@router.post("/")
def ask_question(payload: Question):
    question = payload.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Pergunta vazia.")

    keywords = extract_keywords(question)
    if not keywords:
        raise HTTPException(status_code=400, detail="Não foi possível extrair palavras-chave.")

    print(f"🔎 Palavras-chave extraídas: {keywords}")

    documents = search_documents(keywords)
    if not documents:
        return {"response": "Nenhum trecho relevante encontrado."}

    combined_text = " ".join(documents[:50])
    print(f"📄 Texto enviado à LLM: {combined_text[:500]}...")

    prompt = (
        "Com base no seguinte texto, responda à pergunta de forma concisa e sem repetições. "
        "Se a resposta não estiver clara, indique isso.\n\n"
        f"Texto: {combined_text}\n\n"
        f"Pergunta: {question}\n\n"
        "Resposta:"
    )

    response = get_llm_response(prompt)
    return {"response": response}
