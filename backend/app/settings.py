import json
import os
from flask import Blueprint, request, jsonify

# Percorso del file di configurazione
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

# Valori predefiniti se il file non esiste
DEFAULT_CONFIG = {
    "OPENAI_API_KEY": "your_openai_api_key",
    "OPENAI_MODEL": "gpt-4",
    "OLLAMA_BASE_URL": "http://localhost:11434/api/generate",
    "OLLAMA_MODEL": "llama3",
    "HUGGINGFACE_API_TOKEN": "your_huggingface_api_token",
    "HUGGINGFACE_MODEL": "mistral-7b",
    "AZURE_OPENAI_API_KEY": "your_azure_api_key",
    "AZURE_RESOURCE_NAME": "your_azure_resource_name",
    "AZURE_DEPLOYMENT_NAME": "your_azure_deployment_name",
    "AZURE_API_VERSION": "2024-10-21"
}

# Parametri per Azure OpenAI
DEFAULT_CONFIG.update({

})

def load_settings():
    """Carica le impostazioni dal file JSON."""
    if not os.path.exists(CONFIG_FILE):
        save_settings(DEFAULT_CONFIG)  # Se il file non esiste, crea con i valori di default

    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_CONFIG

def save_settings(new_settings):
    """Salva le impostazioni nel file JSON."""
    with open(CONFIG_FILE, "w") as file:
        json.dump(new_settings, file, indent=4)

# Carica le impostazioni all'avvio
SETTINGS = load_settings()

# Creazione del Blueprint per l'API Flask
settings_bp = Blueprint("settings", __name__)

@settings_bp.route("/settings", methods=["GET"])
def get_settings():
    """Restituisce le impostazioni attuali."""
    return jsonify(load_settings())

@settings_bp.route("/settings", methods=["POST"])
def update_settings():
    """Aggiorna le impostazioni nel file JSON."""
    new_config = request.json
    save_settings(new_config)
    return jsonify({"message": "Settings updated successfully"})