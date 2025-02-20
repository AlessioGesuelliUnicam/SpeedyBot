import requests
from app.settings import SETTINGS

class HuggingFaceAPI:
    def __init__(self):
        """
        Inizializza il client Hugging Face utilizzando i parametri da SETTINGS.
        """
        self.model = SETTINGS.get("HUGGINGFACE_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
        self.api_token = SETTINGS.get("HUGGINGFACE_API_TOKEN", "")
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {"Authorization": f"Bearer {self.api_token}"}

    def send_request(self, prompt):
        """
        Invia una richiesta all'API di Hugging Face e restituisce la risposta generata.
        """
        payload = {"inputs": prompt}
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()[0].get('generated_text', "No response generated.")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Hugging Face API communication failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error with Hugging Face API: {e}")