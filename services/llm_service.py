import requests

BASE_URL = "http://127.0.0.1:1234"
COMPLETIONS_ENDPOINT = f"{BASE_URL}/v1/completions"

def get_llm_response(prompt: str) -> str:
    payload = {
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.0,
        "top_p": 0.7,
        "stop": ["\n\n", "A resposta está presente no texto:"],
        "frequency_penalty": 0.8,
        "presence_penalty": 0.7
    }

    try:
        response = requests.post(COMPLETIONS_ENDPOINT, json=payload)
        response.raise_for_status()
        text = response.json().get("choices", [{}])[0].get("text", "").strip()
        return remove_repetitions(text)
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar ao LLM: {e}")
        return "Erro: Falha na conexão com o LLM."

def remove_repetitions(text: str) -> str:
    seen = set()
    result = []
    for sentence in text.split('. '):
        if sentence not in seen:
            seen.add(sentence)
            result.append(sentence)
    return '. '.join(result)
