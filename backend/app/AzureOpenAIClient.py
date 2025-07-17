import requests
import json
from app.settings import SETTINGS

class AzureOpenAIClient:
    def __init__(self):
        self.api_key = SETTINGS["AZURE_OPENAI_API_KEY"]
        self.resource_name = SETTINGS["AZURE_RESOURCE_NAME"]
        self.deployment_name = SETTINGS["AZURE_DEPLOYMENT_NAME"]
        self.api_version = SETTINGS["AZURE_API_VERSION"]
        self.base_url = f"https://{self.resource_name}.openai.azure.com/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"

    def send_request(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "messages": [
                {"role": "system", "content": "Rispondi solo con JSON valido. Non usare markdown, backtick o testo descrittivo fuori dal JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            raw_response = response.json()
            return self.convert_to_ollama_format(raw_response)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Azure OpenAI API communication failed: {e}")

    def convert_to_ollama_format(self, raw_response):
        """Converte la risposta di Azure OpenAI in formato JSON compatibile con Ollama."""
        import re
        raw_text = raw_response.get("choices", [{}])[0].get("message", {}).get("content", "")

        # Rimuove i backtick e estrae solo il JSON puro se presente
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
        if match:
            raw_text = match.group(1)

        try:
            response_json = json.loads(raw_text)
            return response_json if isinstance(response_json, dict) else {
                "response": raw_text,
                "intent": "general",
                "exercise_type": None
            }
        except json.JSONDecodeError:
            return {"response": raw_text, "intent": "general", "exercise_type": None}