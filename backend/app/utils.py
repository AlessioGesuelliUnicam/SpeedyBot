import os
import json
import PyPDF2
from docx import Document
from typing import Dict, Any, Union


def load_documents() -> Dict[str, Union[str, Dict[str, Any]]]:
    """
    Carica e indicizza documenti dalla directory statica degli esercizi.

    Returns:
        Dict: Mappa dei contenuti per tipo di documento, con gestione di più formati.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    exercises_dir = os.path.join(base_dir, "static", "exercises")

    if not os.path.exists(exercises_dir):
        print(f"Directory {exercises_dir} non trovata.")
        return {}

    print(f"Caricamento documenti dalla directory: {exercises_dir}")

    documents = {}

    for filename in os.listdir(exercises_dir):
        file_path = os.path.join(exercises_dir, filename)
        file_ext = filename.split('.')[-1].lower()

        try:
            if file_ext == "pdf":
                documents[filename] = extract_text_from_pdf(file_path)
            elif file_ext == "docx":
                documents[filename] = extract_text_from_docx(file_path)
            elif file_ext == "json":
                documents[filename] = extract_text_from_json(file_path)
        except Exception as e:
            print(f"Errore durante il caricamento del file {filename}: {e}")

    return documents


def extract_text_from_pdf(file_path: str) -> str:
    """
    Estrae il testo da un file PDF.

    Args:
        file_path (str): Percorso del file PDF.

    Returns:
        str: Testo estratto dal PDF.
    """
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_path: str) -> str:
    """
    Estrae il testo da un file DOCX.

    Args:
        file_path (str): Percorso del file DOCX.

    Returns:
        str: Testo estratto dal documento.
    """
    doc = Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text])

def extract_text_from_json(file_path: str) -> Dict[str, Any]:
    """
    Carica un file JSON.

    Args:
        file_path (str): Percorso del file JSON.

    Returns:
        Dict: Contenuto del file JSON.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def search_documents(query: str, documents: Dict[str, Union[str, Dict[str, Any]]]) -> str:
    """
    Cerca una risposta nei documenti caricati.

    Args:
        query (str): Testo da cercare.
        documents (Dict): Documenti caricati.

    Returns:
        str: Risposta trovata o messaggio di errore.
    """
    query = query.lower()

    for doc_name, content in documents.items():
        # Cerca nelle stringhe di testo
        if isinstance(content, str):
            if query in content.lower():
                return f"Informazione trovata nel documento {doc_name}: {content}"

        # Cerca nei dizionari JSON
        elif isinstance(content, dict):
            for key, value in content.items():
                if query in str(value).lower():
                    return f"Informazione trovata nel documento {doc_name}, chiave {key}: {value}"

    return "Spiacente, non ho trovato informazioni pertinenti nei documenti."