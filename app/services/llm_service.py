import requests

base_url = "http://localhost:1234"
completions_endpoint = f"{base_url}/v1/completions"

def get_llm_response(documents, question):
    combined_text = " ".join(documents[:2])

    payload = {
        "prompt": f"Baseado nos documentos abaixo, responda à pergunta:\n{combined_text}\n\nPergunta:\n{question}",
        "max_tokens": 300,
        "temperature": 0.0,
        "top_p": 0.8
    }
    
    response = requests.post(completions_endpoint, json=payload)
    return response.json()["choices"][0]["text"].strip() if response.status_code == 200 else "Erro na API LLM"
