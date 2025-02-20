import requests
import json
from app.settings import SETTINGS

class OpenAIAPI:
    def __init__(self):
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.model = SETTINGS["OPENAI_MODEL"]
        self.api_key = SETTINGS["OPENAI_API_KEY"]

    def send_request(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"OpenAI API communication failed: {e}")