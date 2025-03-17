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
            raw_response = response.json()
            return self.convert_to_ollama_format(raw_response)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"OpenAI API communication failed: {e}")

    def convert_to_ollama_format(self, raw_response):
        """Converte la risposta OpenAI in formato JSON compatibile con Ollama."""
        try:
            if "choices" in raw_response and isinstance(raw_response["choices"], list) and len(raw_response["choices"]) > 0:
                raw_text = raw_response["choices"][0].get("message", {}).get("content", "")
                try:
                    response_json = json.loads(raw_text)
                    return response_json if isinstance(response_json, dict) else {
                        "response": raw_text,
                        "intent": "general",
                        "exercise_type": None
                    }
                except json.JSONDecodeError:
                    return {
                        "response": raw_text,
                        "intent": "general",
                        "exercise_type": None
                    }
            else:
                return {
                    "response": "Invalid response structure from OpenAI API.",
                    "intent": "general",
                    "exercise_type": None
                }
        except Exception as e:
            return {
                "response": f"Error processing response: {str(e)}",
                "intent": "general",
                "exercise_type": None
            }