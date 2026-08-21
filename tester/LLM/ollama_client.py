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
    }

    response = requests.post(OLLAMA_URL, json=payload)

    if response.status_code == 200:
        return response.json()["response"]

    return None
