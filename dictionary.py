import os
import requests

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NEXOS_API_KEY")

def get_models():
    url = "https://api.nexos.ai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_definition(word: str, sentence: str):
    url = "https://api.nexos.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "be06085c-6c1f-421c-8177-d5cad63c9dcc",
        "messages": [
            {
                "role": "user",
                "content": f"Define the word '{word}' as used in the following sentence: {sentence}"
            }
        ],
        "max_tokens": 128,
        "temperature": 1,
        "top_p": 1,
        "n": 1,
        "response_format": {"type": "text"}
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()["choices"][0]["message"]["content"].strip()
    return result