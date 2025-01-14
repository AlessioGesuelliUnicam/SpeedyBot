import requests
import json


class OllamaAPI:
    def __init__(self, base_url="http://localhost:11434/api/generate", model="llama3"):
        self.base_url = base_url
        self.model = model

    def send_request(self, prompt, stream=True, timeout=60):
        """
        Sends a request to the Ollama API and returns the response as a string.
        """
        payload = {"model": self.model, "prompt": prompt}
        try:
            response = requests.post(
                self.base_url, json=payload, stream=stream, timeout=timeout
            )
            response.raise_for_status()

            if stream:
                return self._parse_stream_response(response)
            else:
                return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API communication failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error with Ollama API: {e}")

    def _parse_stream_response(self, response):
        """
        Parses the streaming response and combines it into a single string.
        """
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
        if not full_response.strip():
            raise ValueError("Ollama API returned an empty or invalid response")
        return full_response.strip()