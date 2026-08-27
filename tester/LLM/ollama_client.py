import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def send_prompt(
    model_name,
    prompt,
):

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": 1024, "temperature": 0.3},
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)

    if response.status_code == 200:
        return response.json()["response"]

    return None
