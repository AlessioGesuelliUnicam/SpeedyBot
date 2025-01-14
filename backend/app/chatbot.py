from flask import Blueprint, request, jsonify, url_for, current_app
import json, re, os, random
from app.models import ExerciseType, ExerciseWithImage
from app import db
from .utils import load_documents, search_documents
from .ollama_client import OllamaAPI
from docx import Document
import PyPDF2

chatbot_bp = Blueprint('chatbot', __name__)

# Inizializza il client di Ollama
ollama_client = OllamaAPI()

DOCUMENTS = load_documents()

exercise_cache = None

def fetch_exercise_types(use_cache=True):
    global exercise_cache
    if use_cache and exercise_cache:
        print("[fetch_exercise_types] Using cached exercises.")
        return exercise_cache

    print("[fetch_exercise_types] Querying database for exercises.")
    exercise_types = ExerciseType.query.all()
    exercise_cache = [
        {
            "id": et.id,
            "exerciseType": et.exerciseType,
            "normalizedType": et.exerciseType.strip().lower(),
            "exerciseWithImage": et.exerciseWithImage,
            "prompt": et.prompt,
        }
        for et in exercise_types
    ]
    print(f"[fetch_exercise_types] Loaded exercises: {exercise_cache}")
    return exercise_cache


class GlobalStateManager:
    def reset_current_question(self):
        """Reset the current question to prepare for the next iteration."""
        self.current_question = None
        print("[GlobalStateManager] Current question reset.")

    def prepare_next_question(self):
        """Prepare the next question for the exercise if applicable."""
        if self.current_exercise:
            print(f"[GlobalStateManager] Preparing next question for {self.current_exercise}.")
            # Example logic to fetch a next question
            self.current_question = {
                "expected_response": "gatto",
                "image_url": "/static/uploads/animals/gatto.jpg",
                "animal_name": "cat",
            }
            return self.current_question
        else:
            print("[GlobalStateManager] No exercise set.")
            return None

    def __init__(self):
        self.current_exercise = None
        self.current_question = None
        self.pending_exercise = None
        self.learning_context = None

    def set_learning_context(self, context):
        """Set the current learning context to provide more targeted responses."""
        self.learning_context = context

    def clear_learning_context(self):
        """Clear the current learning context."""
        self.learning_context = None

    def set_pending_exercise(self, exercise_type):
        if self.current_exercise:
            raise ValueError("Un esercizio è già in corso. Termina o annulla prima di iniziarne uno nuovo.")
        self.pending_exercise = exercise_type
        print(f"[GlobalStateManager] Pending exercise set to: {self.pending_exercise}")

    def clear_pending_exercise(self):
        print("[GlobalStateManager] Clearing pending exercise.")
        self.pending_exercise = None

    def set_current_exercise(self, exercise_id, exercise_type):
        """Set the current active exercise."""
        self.current_exercise = {"id": exercise_id, "type": exercise_type}
        print(f"[GlobalStateManager] Current exercise set to: {self.current_exercise}")

    def reset_current_exercise(self):
        """Reset the current exercise state."""
        print("[GlobalStateManager] Resetting current exercise.")
        self.current_exercise = None
        self.current_question = None

    def set_current_question(self, question_data):
        """Set the current question for the active exercise."""
        self.current_question = question_data
        print(f"[GlobalStateManager] Current question set: {question_data}")

global_state_manager = GlobalStateManager()

def handle_exception(e, message="Si è verificato un errore."):
    print(f"[Error] {message}: {e}")
    return jsonify({"error": message, "details": str(e)}), 500

def extract_json_from_response(response):
    try:
        matches = re.findall(r"\{.*?\}", response, re.DOTALL)
        for match in matches:
            try:
                json_content = json.loads(match)
                if "intent" in json_content and "response" in json_content:
                    return json_content
            except json.JSONDecodeError:
                continue
        raise ValueError("No valid JSON containing intent and response found.")
    except Exception as e:
        print(f"[extract_json_from_response] Error: {e}")
        return {
            "intent": "general",
            "response": "Non ho capito la tua domanda.",
            "exercise_type": None,
        }

def identify_intent(user_message, learning_context=None):
    try:
        print(f"[identify_intent] Received user message: {user_message}")
        exercises = fetch_exercise_types()
        exercises_type = [et["exerciseType"] for et in exercises]
        exercises_type_str = ", ".join(exercises_type)
        print(f"[identify_intent] Available exercises: {exercises_type_str}")

        context_prompt = (
            f"You are an educational chatbot for German-speaking Swiss train drivers learning technical Italian "
            f"for operations in Ticino. Current context: {learning_context or 'None'}\n\n"
        )

        prompt = f"""{context_prompt}
        The user said: "{user_message}"

        Tasks:
        1. Identify the user's intent:
           - "general": for casual conversations (e.g., "Ciao", "Come stai?")
           - "learn": for learning technical Italian (e.g., "Come si dice 'Hund' in italiano?")
           - "exercise": for practicing language skills (e.g., "Voglio fare un esercizio").
             Available exercises: {exercises_type_str}

        2. If the intent is unclear, suggest asking more specific questions.
        3. If the user mentions an exercise type, confirm it.

        Respond as JSON:
        {{
            "intent": "general|learn|exercise|clarify",
            "response": "Short and conversational response",
            "exercise_type": "Optional specific exercise type if applicable",
            "additional_context": "Optional additional information"
        }}
        """
        print(f"[identify_intent] Sending prompt to LLM: {prompt}")
        raw_response = ollama_client.send_request(prompt)
        print(f"[identify_intent] Raw response from LLM: {raw_response}")

        parsed_response = extract_json_from_response(raw_response)
        print(f"[identify_intent] Parsed response: {parsed_response}")
        return parsed_response

    except Exception as e:
        print(f"[identify_intent] Error: {e}")
        return {
            "intent": "general",
            "response": "Non ho capito bene. Puoi ripetere o specificare meglio?",
            "exercise_type": None,
        }

def extract_structured_data(response):
    """
    Estrae dati strutturati (intent, response, exercise_type) da una risposta in formato testo libero.

    Args:
        response (str): La risposta fornita dall'LLM.

    Returns:ba
        dict: Dati strutturati contenenti intent, response e exercise_type.
    """
    try:
        intent_match = re.search(r"\*\*Intent:\*\* (.*?)\n", response)
        response_match = re.search(r"\*\*Response:\*\* (.*?)\n", response)
        exercise_type_match = re.search(r"\*\*Exercise_type:\*\* (.*?)\n", response)

        intent = intent_match.group(1).strip() if intent_match else "general"
        llm_response = response_match.group(1).strip() if response_match else "Non ho capito la tua domanda."
        exercise_type = exercise_type_match.group(1).strip() if exercise_type_match else None

        return {
            "intent": intent,
            "response": llm_response,
            "exercise_type": exercise_type,
        }
    except Exception as e:
        print(f"[extract_structured_data] Error: {e}")
        return {
            "intent": "general",
            "response": "Non ho capito la tua domanda.",
            "exercise_type": None,
        }

def load_exercise_content(exercise_type):
    exercise_type_normalized = exercise_type.lower().replace(' ', '_')
    file_path = os.path.join(current_app.root_path, 'static', 'exercises', exercise_type_normalized)

    print(f"[load_exercise_content] Generating path: {file_path}")

    try:
        if os.path.exists(f"{file_path}.json"):
            with open(f"{file_path}.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        elif os.path.exists(f"{file_path}.docx"):
            document = Document(f"{file_path}.docx")
            return "\n".join([para.text for para in document.paragraphs])
        elif os.path.exists(f"{file_path}.pdf"):
            with open(f"{file_path}.pdf", 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return "\n".join([page.extract_text() for page in reader.pages])

        raise FileNotFoundError(f"File for exercise '{exercise_type}' not found.")
    except FileNotFoundError as e:
        print(f"[load_exercise_content] File not found: {e}")
        return None
    except Exception as e:
        print(f"[load_exercise_content] Error loading content: {e}")
        return None

def handle_learning_request(user_message, documents):
    """
    Handle learning requests by searching documents and generating a response.

    Args:
        user_message (str): User's learning query
        documents (dict): Loaded documents

    Returns:
        dict: Learning response with found information
    """
    # Search documents for relevant information
    document_search_result = search_documents(user_message, documents)

    # Use Ollama to generate a comprehensive response
    prompt = f"""
    Context: You are helping a German-speaking train driver learn technical Italian.

    Document search result: {document_search_result}

    User query: {user_message}

    Generate a clear, concise explanation that helps the user understand the topic,
    incorporating information from the document search if possible.
    """

    try:
        llm_response = ollama_client.send_request(prompt)
        return {"message": llm_response}
    except Exception as e:
        print(f"[handle_learning_request] Error: {e}")
        return {"message": "I'm having trouble finding information about that. Could you rephrase your question?"}

def evaluate_with_llm(user_response, expected_response):
    """
    Utilizza un LLM per valutare la somiglianza tra la risposta dell'utente e quella attesa.

    Args:
        user_response (str): La risposta fornita dall'utente.
        expected_response (str): La risposta attesa.

    Returns:
        dict: Un dizionario contenente il punteggio di somiglianza e un suggerimento.
    """
    prompt = f"""
    Sei un assistente didattico che valuta risposte in italiano. 
    Confronta la risposta dell'utente con quella attesa e determina se la risposta dell'utente è corretta o quasi corretta.

    Risposta attesa: "{expected_response}"
    Risposta dell'utente: "{user_response}"

    Valuta:
    1. La correttezza semantica (la risposta ha lo stesso significato?).
    2. Errori grammaticali minori (sono accettabili se non cambiano il significato).

    Rispondi in JSON con il seguente formato:
    {{
        "correct": true|false,
        "feedback": "Commento sulla risposta (cosa è corretto o cosa manca)."
    }}
    """
    try:
        response = ollama_client.send_request(prompt)
        return json.loads(response)  # Parsing del JSON restituito
    except Exception as e:
        print(f"[evaluate_with_llm] Error: {e}")
        return {"correct": False, "feedback": "Errore nella valutazione con LLM."}

def generate_textual_exercise(exercise_type):
    try:
        content = load_exercise_content(exercise_type)
        if not content or not isinstance(content, dict):
            raise ValueError(f"Formato non valido per il file dell'esercizio '{exercise_type}'.")

        key = exercise_type.lower().replace(" ", "_")
        if isinstance(content, dict) and key in content:
            questions = content[key]
            if not questions:
                raise ValueError("Nessuna domanda trovata nel file JSON.")

            question = random.choice(questions)

            # Debug del contenuto della domanda
            print(f"[generate_textual_exercise] Selected question: {question}")

            return {
                "question": question.get("question", "Domanda non trovata."),
                "answer": question.get("solution", "Risposta non trovata.").strip().lower()
            }

        raise ValueError(f"Formato del contenuto per '{exercise_type}' non supportato.")
    except Exception as e:
        print(f"[generate_textual_exercise] Error: {e}")
        return {"question": "Non sono riuscito a generare un esercizio. Riprova più tardi.", "answer": ""}

def start_exercise(exercise, prompt=None):
    try:
        print(f"[start_exercise] Starting exercise: {exercise}")
        if not exercise:
            raise ValueError("L'esercizio specificato non è valido.")

        exercise_type = exercise.get("exerciseType") or exercise.get("type")
        if not exercise_type:
            raise KeyError(f"Il campo 'type' o 'exerciseType' è mancante. Dati ricevuti: {exercise}")

        prompt = prompt or exercise.get("prompt", "Inizia l'esercizio!")
        print(f"[start_exercise] Exercise type: {exercise_type}, Prompt: {prompt}")

        # Gestione per esercizi con immagini
        if exercise.get("exerciseWithImage", False):
            print("[start_exercise] Detected image-based exercise.")
            image_entry = ExerciseWithImage.query.filter_by(exercise_type_id=exercise["id"]).order_by(
                db.func.random()).first()
            if not image_entry:
                raise ValueError("Nessuna immagine disponibile per questo esercizio.")

            # Imposta la domanda corrente nel GlobalStateManager
            global_state_manager.set_current_question({
                "expected_response": image_entry.description_it,
                "image_url": image_entry.file_path,
                "animal_name": image_entry.description_en,
            })

            # Prepara il messaggio per l'utente
            return {
                "message": f"Guarda l'immagine e rispondi: "
                           f"\"Wie sagt man '{image_entry.description_en}' auf Italienisch?\"",
                "image": url_for('static', filename=image_entry.file_path.split('static/')[-1], _external=True),
            }

        # Gestione per esercizi testuali
        print("[start_exercise] Detected textual exercise.")
        exercise_data = generate_textual_exercise(exercise_type)
        if not exercise_data or "question" not in exercise_data:
            raise ValueError("Errore nella generazione dell'esercizio testuale.")

        question = exercise_data.get("question", "")
        correct_answer = exercise_data.get("answer", "")
        print(f"[start_exercise] Generated question: {question}, Expected answer: {correct_answer}")

        # Imposta la domanda corrente
        global_state_manager.set_current_question({
            "expected_response": correct_answer,
            "question": question,
        })

        return {"message": f"Domanda: {question}", "image": None}

    except Exception as e:
        print(f"[start_exercise] Error: {e}")
        return {"error": f"Errore durante l'avvio dell'esercizio: {str(e)}"}


@chatbot_bp.route('/evaluate', methods=['POST'])
def evaluate_response():
    data = request.json
    user_response = data.get('response', '').strip().lower()

    # Funzione per normalizzare il testo
    def normalize_text(text):
        import unicodedata
        return ''.join(
            c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'
        ).strip().lower()

    # Recupera la domanda corrente
    current_question = global_state_manager.current_question
    if not current_question:
        return jsonify({"message": "Nessuna domanda attiva al momento."}), 400

    # Normalizza le risposte
    expected_response = normalize_text(current_question.get('expected_response', '').strip())
    user_response_normalized = normalize_text(user_response)

    # Debugging delle risposte
    print(f"[evaluate_response] User response: '{user_response}', Expected response: '{expected_response}'")

    # Risposta corretta
    if user_response_normalized == expected_response:
        feedback = f"✔️ Corretto! La risposta è '{expected_response}'."

        # Esercizio basato su immagini
        if global_state_manager.current_exercise.get('exerciseWithImage', False):
            print("[evaluate_response] Image-based exercise detected, loading next image.")
            # Carica una nuova immagine casuale
            image_entry = ExerciseWithImage.query.filter_by(
                exercise_type_id=global_state_manager.current_exercise['id']
            ).order_by(db.func.random()).first()

            if not image_entry:
                # Termina l'esercizio se non ci sono altre immagini
                global_state_manager.reset_current_exercise()
                return jsonify({
                    "feedback": feedback,
                    "message": "Non ci sono altre immagini disponibili per questo esercizio. Vuoi scegliere un altro esercizio?"
                })

            # Imposta la nuova domanda corrente
            global_state_manager.set_current_question({
                "expected_response": image_entry.description_it,
                "image_url": image_entry.file_path,
                "animal_name": image_entry.description_en,
            })

            return jsonify({
                "feedback": feedback,
                "next_question": (
                    f"Guarda l'immagine e rispondi: "
                    f"\"Wie sagt man '{image_entry.description_en}' auf Italienisch?\""
                ),
                "image": url_for('static', filename=image_entry.file_path.split('static/')[-1], _external=True),
            })

        # Esercizio testuale
        else:
            print("[evaluate_response] Textual exercise detected, generating next question.")
            exercise_type = global_state_manager.current_exercise.get('type')
            next_question = generate_textual_exercise(exercise_type)

            if next_question and "question" in next_question:
                global_state_manager.set_current_question({
                    "expected_response": next_question.get("answer", ""),
                    "question": next_question.get("question", ""),
                })
                return jsonify({
                    "feedback": feedback,
                    "next_question": next_question.get("question", ""),
                })

            # Se non ci sono domande disponibili
            global_state_manager.reset_current_exercise()
            return jsonify({
                "feedback": feedback,
                "message": "Non ci sono altre domande per questo esercizio. Vuoi scegliere un altro esercizio?"
            })

    # Risposta errata
    else:
        return jsonify({
            "feedback": f"❌ Errato. La risposta corretta era '{expected_response}'.",
            "question": current_question.get("question", ""),
        })

@chatbot_bp.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    user_message = data.get('message', '').strip().lower()
    print(f"[chatbot] Received user message: {user_message}")

    def evaluate_response_internal(user_message):
        # Recupera la domanda corrente dal GlobalStateManager
        current_question = global_state_manager.current_question
        if not current_question:
            return jsonify({"message": "Nessuna domanda attiva al momento."}), 400

        expected_response = current_question.get('expected_response', '').strip()

        # Usa il modello LLM per valutare la risposta
        evaluation = evaluate_with_llm(user_message, expected_response)

        if evaluation.get("correct", False):
            feedback = f"✔️ Corretto! {evaluation.get('feedback', '')}"

            # Genera una nuova domanda
            exercise_type = global_state_manager.current_exercise.get('type')
            next_question = generate_textual_exercise(exercise_type)

            if next_question and "question" in next_question:
                global_state_manager.set_current_question({
                    "expected_response": next_question.get("answer", ""),
                    "question": next_question.get("question", ""),
                })
                return jsonify({
                    "feedback": feedback,
                    "next_question": next_question.get("question", ""),
                })
            else:
                global_state_manager.reset_current_exercise()
                return jsonify({
                    "feedback": feedback,
                    "message": "Non ci sono altre domande per questo esercizio. Vuoi scegliere un altro esercizio?"
                })

        else:
            feedback = f"❌ Errato. {evaluation.get('feedback', 'La risposta non è corretta.')}"
            return jsonify({
                "feedback": feedback,
                "question": current_question.get("question", "")
            })

    try:
        # Se c'è una domanda corrente, considera il messaggio dell'utente come risposta
        if global_state_manager.current_question:
            print("[chatbot] Current question detected, evaluating response.")
            return evaluate_response_internal(user_message)

        if global_state_manager.current_exercise:
            return jsonify(start_exercise(global_state_manager.current_exercise))

        # Caso speciale: continuazione di un esercizio esistente
        if user_message == "continua esercizio":
            current_exercise = global_state_manager.current_exercise
            if not current_exercise:
                return jsonify({"message": "Non c'è un esercizio attivo. Inizia un nuovo esercizio."}), 400
            return jsonify(start_exercise(current_exercise))

        # Gestione della conferma di un esercizio in sospeso
        if global_state_manager.pending_exercise:
            if user_message in ["sì", "si", "ok"]:
                exercise_type_name = global_state_manager.pending_exercise
                exercises = fetch_exercise_types()
                exercise = next((et for et in exercises if et["exerciseType"].lower() == exercise_type_name.lower()), None)
                if not exercise:
                    global_state_manager.clear_pending_exercise()
                    return jsonify({"message": f"L'esercizio '{exercise_type_name}' non è stato trovato."}), 404
                global_state_manager.set_current_exercise(exercise["id"], exercise_type_name)
                global_state_manager.clear_pending_exercise()
                return jsonify(start_exercise(exercise))
            else:
                global_state_manager.clear_pending_exercise()
                return jsonify({"message": "Esercizio annullato. Scegli un'altra attività."})

        # Identifica l'intento dell'utente
        intent_data = identify_intent(user_message, global_state_manager.learning_context)
        print(f"[chatbot] Intent data: {intent_data}")
        intent = intent_data.get('intent', 'general')
        print(f"[chatbot] Identified intent: {intent}")

        # Gestione degli intenti
        if intent == 'learn':
            response = handle_learning_request(user_message, DOCUMENTS)
            global_state_manager.set_learning_context(user_message)
            print("[chatbot] Handling learning request.")
            return jsonify(response)

        elif intent == 'exercise':
            # Logica per selezionare esercizi dal database
            exercise_types = intent_data.get('exercise_type', [])
            print(f"[chatbot] Exercise types detected: {exercise_types}")
            if isinstance(exercise_types, str):
                exercise_types = [et.strip() for et in exercise_types.split(',')]
            elif not isinstance(exercise_types, list):
                exercise_types = []

            db_exercises = fetch_exercise_types()
            db_exercise_types = [et["exerciseType"].lower() for et in db_exercises]

            # Verifica quali esercizi sono disponibili
            available_exercises = [ex for ex in exercise_types if ex.lower() in db_exercise_types]

            if not available_exercises:
                db_exercise_names = [et["exerciseType"] for et in db_exercises]
                return jsonify({
                    "message": "L'esercizio richiesto non è disponibile. Ecco gli esercizi che puoi scegliere: " +
                               ", ".join(db_exercise_names)
                })
            elif len(available_exercises) == 1:
                exercise_type_name = available_exercises[0]
                global_state_manager.set_pending_exercise(exercise_type_name)
                return jsonify({"message": f"Hai scelto l'esercizio '{exercise_type_name}'. Conferma scrivendo 'sì'."})
            else:
                return jsonify({
                    "message": f"Puoi scegliere tra i seguenti esercizi disponibili: {', '.join(available_exercises)}"
                })

        elif intent == 'general':
            response = intent_data.get('response', "Ciao! Come posso aiutarti oggi?")
            activity_suggestion = "Puoi provare un esercizio come 'Fill with Imperative' o chiedermi qualcosa in italiano tecnico."
            print("[chatbot] Handling general intent.")
            return jsonify({"message": f"{response} {activity_suggestion}"})

        else:
            return jsonify({"message": intent_data.get('response', "Come posso aiutarti oggi?")})

    except Exception as e:
        print(f"[chatbot] General error: {e}")
        return jsonify({"message": "Si è verificato un errore. Per favore, riprova."}), 500


