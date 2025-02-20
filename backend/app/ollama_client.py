import requests
import json
from app.settings import SETTINGS

class OllamaAPI:
    def __init__(self):
        self.base_url = SETTINGS["OLLAMA_BASE_URL"]
        self.model = SETTINGS["OLLAMA_MODEL"]

    def send_request(self, prompt, stream=True, timeout=60):
        payload = {"model": self.model, "prompt": prompt}
        try:
            response = requests.post(self.base_url, json=payload, stream=stream, timeout=timeout)
            response.raise_for_status()

            if stream:
                return self._parse_stream_response(response)
            else:
                return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API communication failed: {e}")

    def _parse_stream_response(self, response):
        full_response = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8").strip()
                try:
                    json_data = json.loads(decoded_line)
                    if "response" in json_data:
                        full_response += json_data["response"]
                except json.JSONDecodeError:
                    continue
        return full_response.strip() if full_response.strip() else "Error: Empty response from Ollama API"