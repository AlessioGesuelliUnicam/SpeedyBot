import os
import json
import PyPDF2
from docx import Document
from typing import Dict, Any, Union


def load_documents() -> Dict[str, Union[str, Dict[str, Any]]]:
    """
    Loads and indexes documents from the static exercises directory.

    Returns:
        Dict: Map of contents by document type, handling multiple formats.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    exercises_dir = os.path.join(base_dir, "static", "exercises")

    if not os.path.exists(exercises_dir):
        print(f"Directory {exercises_dir} not found.")
        return {}

    print(f"Loading documents from directory: {exercises_dir}")

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
            print(f"Error loading file {filename}: {e}")

    return documents


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts text from a DOCX file.

    Args:
        file_path (str): Path to the DOCX file.

    Returns:
        str: Extracted text from the document.
    """
    doc = Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text])

def extract_text_from_json(file_path: str) -> Dict[str, Any]:
    """
    Loads a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        Dict: Content of the JSON file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def search_documents(query: str, documents: Dict[str, Union[str, Dict[str, Any]]]) -> str:
    """
    Searches for a query within the loaded documents.

    Args:
        query (str): Text to search for.
        documents (Dict): Loaded documents.

    Returns:
        str: Found response or error message.
    """
    query = query.lower()

    for doc_name, content in documents.items():
        # Search in text strings
        if isinstance(content, str):
            if query in content.lower():
                return f"Information found in document {doc_name}: {content}"

        # Search in JSON dictionaries
        elif isinstance(content, dict):
            for key, value in content.items():
                if query in str(value).lower():
                    return f"Information found in document {doc_name}, key {key}: {value}"

    return "Sorry, no relevant information was found in the documents."