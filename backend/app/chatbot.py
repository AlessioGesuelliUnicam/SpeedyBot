from flask import Blueprint, request, jsonify, url_for, current_app
import json, re, os, random
from app.models import ExerciseType, ExerciseWithImage
from app import db
from .utils import load_documents, search_documents
from .ollama_client import OllamaAPI
from .openAI_client import OpenAIAPI
from .huggingface_client import HuggingFaceAPI
from docx import Document
import PyPDF2

chatbot_bp = Blueprint('chatbot', __name__)

# Initialize the Ollama client
#ollama_client = OllamaAPI()

# Initialize the OpenAI client
#gpt_client = OpenAIAPI()

# Initialize the HuggingFace client
#huggingface_client = HuggingFaceAPI()


DOCUMENTS = load_documents()

exercise_cache = None

# Client disponibili
llm_clients = {
    "ollama": OllamaAPI(),
    "gpt": OpenAIAPI(),
    "huggingface": HuggingFaceAPI()
}

# Stato globale per il modello selezionato
class ModelManager:
    def __init__(self):
        self.selected_model = "ollama"  # Modello di default

    def set_model(self, model_name):
        if model_name in llm_clients:
            self.selected_model = model_name
            return f"Modello impostato su {model_name}"
        return "Modello non riconosciuto"

    def get_client(self):
        return llm_clients[self.selected_model]

model_manager = ModelManager()

@chatbot_bp.route('/set-model', methods=['POST'])
def set_model():
    """ API per cambiare il modello LLM """
    data = request.json
    model_name = data.get("model", "").lower()
    response = model_manager.set_model(model_name)
    return jsonify({"message": response})

    llm_client = model_manager.get_client()


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
        """Prepara la prossima domanda per l'esercizio."""
        if self.current_exercise:
            print(f"[GlobalStateManager] Preparando la prossima domanda per {self.current_exercise}.")

            # Controlla se l'esercizio è testuale o con immagini
            exercise_type = self.current_exercise["type"]
            exercises = fetch_exercise_types()
            exercise_data = next((ex for ex in exercises if ex["exerciseType"].lower() == exercise_type.lower()), None)

            if not exercise_data:
                print("[GlobalStateManager] Errore: Tipo di esercizio non trovato nel database.")
                return None

            if exercise_data["exerciseWithImage"]:
                # Esercizio con immagine: recupera una nuova immagine e la domanda
                print("[GlobalStateManager] Esercizio con immagini rilevato, recupero una nuova immagine.")
                image_entry = ExerciseWithImage.query.filter_by(exercise_type_id=exercise_data["id"]).order_by(
                    db.func.random()).first()

                if not image_entry:
                    print("[GlobalStateManager] Nessuna immagine trovata per questo esercizio.")
                    return None

                return {
                    "question": f"Osserva l'immagine e rispondi: {image_entry.description_it}",
                    "expected_response": image_entry.description_it.strip().lower(),
                    "image_url": image_entry.file_path
                }

            else:
                # Esercizio testuale: recupera la prossima domanda dal file JSON
                print("[GlobalStateManager] Esercizio testuale rilevato, recupero una nuova domanda.")
                question = generate_textual_exercise(self.current_exercise["type"])

                if question:
                    return {
                        "question": question["question"],
                        "expected_response": question["answer"]
                    }
                else:
                    return None  # Se non ci sono più domande

        print("[GlobalStateManager] Nessun esercizio attivo.")
        return None

    def __init__(self):
        self.current_exercise = None
        self.current_question = None
        self.pending_exercise = None
        self.learning_context = None
        self.attempts = 0  # Inizializza il contatore dei tentativi

    def set_current_question(self, question_data):
        """Setta la domanda attuale e resetta i tentativi."""
        self.current_question = question_data
        self.attempts = 0  # Resetta il conteggio dei tentativi
        print(f"[GlobalStateManager] Current question set: {question_data}")

    def increment_attempts(self):
        """Incrementa il contatore dei tentativi."""
        self.attempts += 1

    def reset_attempts(self):
        """Resetta il contatore dei tentativi."""
        self.attempts = 0
    def set_learning_context(self, context):
        """Set the current learning context to provide more targeted responses."""
        self.learning_context = context

    def clear_learning_context(self):
        """Clear the current learning context."""
        self.learning_context = None

    def set_pending_exercise(self, exercise_type):
        if self.current_exercise:
            raise ValueError("An exercise is already in progress. Finish or cancel it before starting a new one.")
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

    # Removed duplicate set_current_question method.

global_state_manager = GlobalStateManager()

def handle_exception(e, message="An error occurred."):
    print(f"[Error] {message}: {e}")
    return jsonify({"error": message, "details": str(e)}), 500


def extract_json_from_response(response):
    try:
        print(f"[extract_json_from_response] Raw LLM response: {response}")  # Debug

        # Se la risposta è un dizionario, estrai il contenuto JSON
        if isinstance(response, dict):
            return response

        # Controlla se la risposta inizia con un testo extra (es. "Here is the response:\n")
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            response_content = match.group(0)
        else:
            raise ValueError("Nessun JSON valido trovato nella risposta.")

        json_content = json.loads(response_content)

        if "intent" in json_content and "response" in json_content:
            return json_content
        else:
            raise ValueError("Il JSON ricevuto non contiene 'intent' o 'response'.")

    except json.JSONDecodeError as e:
        print(f"[extract_json_from_response] JSON decoding error: {e}")
        return {
            "intent": "general",
            "response": "Non ho capito bene. Puoi ripetere o specificare meglio?",
            "exercise_type": None,
        }
    except Exception as e:
        print(f"[extract_json_from_response] Unexpected error: {e}")
        return {
            "intent": "general",
            "response": "Errore nell'elaborazione della risposta.",
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
            f"You are an educational chatbot assisting German-speaking Swiss train drivers "
            f"in learning technical Italian for operations in Ticino. Current context: {learning_context or 'None'}\n\n"
        )

        prompt = f"""{context_prompt}
        The user said: "{user_message}"

        Tasks:
        1. Identify the user's intent:
           - "general": for casual conversations (e.g., "Hi", "How are you?")
           - "learn": for learning technical Italian (e.g., "How do you say 'dog' in Italian?")
           - "exercise": for practicing language skills (e.g., "I want to do an exercise").
             Available exercises: {exercises_type_str}

        2. If the user explicitly mentions an exercise type, set intent to "exercise".
        3. If intent is unclear, respond with "clarify" and suggest asking a more specific question.

        Respond strictly in this JSON format:
        {{
            "intent": "general|learn|exercise|clarify",
            "response": "Short and conversational response",
            "exercise_type": "Optional specific exercise type if applicable",
            "additional_context": "Optional additional information"
        }}
        """
        print(f"[identify_intent] Sending prompt to LLM: {prompt}")

        llm_client = model_manager.get_client()
        raw_response = llm_client.send_request(prompt)
        print(f"[identify_intent] Raw response from LLM: {raw_response}")

        parsed_response = extract_json_from_response(raw_response)
        print(f"[identify_intent] Parsed response: {parsed_response}")
        return parsed_response

    except Exception as e:
        print(f"[identify_intent] Error: {e}")
        return {
            "intent": "general",
            "response": "I didn't understand well. Could you repeat or specify better?",
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
        llm_client = model_manager.get_client()
        #llm_response = ollama_client.send_request(prompt)
        #llm_response = gpt_client.send_request(prompt)
        #llm_response = huggingface_client.send_request(prompt)
        llm_response = llm_client.send_request(prompt)

        return {"message": llm_response}

    except Exception as e:

        print(f"[handle_learning_request] Error: {e}")

        return {"message": "I'm having trouble finding information about that. Could you rephrase your question?"}


def evaluate_with_llm(user_response, expected_response):
    user_response_normalized = user_response.strip().lower()
    expected_response_normalized = expected_response.strip().lower()

    if user_response_normalized == expected_response_normalized:
        return {
            "correct": True,
            "feedback": f"✔️ '{user_response}' è la risposta giusta."
        }

    # Se la risposta non è esatta, chiama l'LLM per valutare
    prompt = f"""
    You are a teaching assistant evaluating answers in Italian.
    Compare the user's response with the expected one and determine if it is correct.

    Expected response: "{expected_response}"
    User's response: "{user_response}"
    
    ⚠️ **IMPORTANT:** Under no circumstances should you reveal the correct answer in your response. Do not include the expected answer or any hints that could give it away.
    
    Only return `"correct": true` if the answer exactly matches the expected response.
    
    Speak in informal Italian and provide a brief explanation without revealing the answer.
    Respond in JSON:
    {{
        "correct": true|false,
        "feedback": "Explanation without revealing the answer."
    }}
    """
    try:
        llm_client = model_manager.get_client()
        response = llm_client.send_request(prompt)
        json_response = json.loads(response) if isinstance(response, str) else response

        if "correct" in json_response and "feedback" in json_response:
            return json_response

    except Exception as e:
        print(f"[evaluate_with_llm] Error: {e}")

    return {"correct": False, "feedback": "Errore nell'elaborazione della risposta. Prova di nuovo."}


def generate_textual_exercise(exercise_type):
    try:

        content = load_exercise_content(exercise_type)

        if not content or not isinstance(content, dict):
            raise ValueError(f"Invalid format for exercise file '{exercise_type}'.")

        key = exercise_type.lower().replace(" ", "_")

        if isinstance(content, dict) and key in content:

            questions = content[key]

            if not questions:
                raise ValueError("No questions found in the JSON file.")

            question = random.choice(questions)

            # Debug the question content

            print(f"[generate_textual_exercise] Selected question: {question}")

            return {

                "question": question.get("question", "Question not found."),

                "answer": question.get("solution", "Answer not found.").strip().lower()

            }

        raise ValueError(f"Unsupported content format for '{exercise_type}'.")

    except Exception as e:

        print(f"[generate_textual_exercise] Error: {e}")

        return {"question": "I couldn't generate an exercise. Please try again later.", "answer": ""}


def start_exercise(exercise, prompt=None):
    try:

        print(f"[start_exercise] Starting exercise: {exercise}")

        if not exercise:
            raise ValueError("The specified exercise is invalid.")

        exercise_type = exercise.get("exerciseType") or exercise.get("type")

        if not exercise_type:
            raise KeyError(f"The 'type' or 'exerciseType' field is missing. Received data: {exercise}")

        prompt = prompt or exercise.get("prompt", "Start the exercise!")

        print(f"[start_exercise] Exercise type: {exercise_type}, Prompt: {prompt}")

        # Handling image-based exercises

        if exercise.get("exerciseWithImage", False):

            print("[start_exercise] Detected image-based exercise.")

            image_entry = ExerciseWithImage.query.filter_by(exercise_type_id=exercise["id"]).order_by(

                db.func.random()).first()

            if not image_entry:
                raise ValueError("No images available for this exercise.")

            # Set the current question in the GlobalStateManager

            global_state_manager.set_current_question({

                "expected_response": image_entry.description_it,

                "image_url": image_entry.file_path,

                "animal_name": image_entry.description_en,

            })

            # Prepare the message for the user

            return {

                "message": f"Look at the image and answer: "

                           f"\"Wie sagt man '{image_entry.description_en}' auf Italienisch?\"",

                "image": url_for('static', filename=image_entry.file_path.split('static/')[-1], _external=True),

            }

        # Handling textual exercises

        print("[start_exercise] Detected textual exercise.")

        exercise_data = generate_textual_exercise(exercise_type)

        if not exercise_data or "question" not in exercise_data:
            raise ValueError("Error generating textual exercise.")

        question = exercise_data.get("question", "")

        correct_answer = exercise_data.get("answer", "")

        print(f"[start_exercise] Generated question: {question}, Expected answer: {correct_answer}")

        # Set the current question

        global_state_manager.set_current_question({

            "expected_response": correct_answer,

            "question": question,

        })

        return {"message": f"Question: {question}", "image": None}


    except Exception as e:

        print(f"[start_exercise] Error: {e}")

        return {"error": f"Error starting exercise: {str(e)}"}

def handle_image_exercise(exercise):
    """Handles the initialization of an image-based exercise."""
    print("[handle_image_exercise] Handling image-based exercise.")

    image_entry = ExerciseWithImage.query.filter_by(exercise_type_id=exercise["id"]).order_by(
        db.func.random()).first()

    if not image_entry:
        raise ValueError("No images available for this exercise.")

    global_state_manager.set_current_question({
        "expected_response": image_entry.description_it,
        "image_url": image_entry.file_path,
        "animal_name": image_entry.description_en,
    })

    return {
        "message": f"Look at the image and answer: \"Wie sagt man '{image_entry.description_en}' auf Italienisch?\"",
        "image": url_for('static', filename=image_entry.file_path.split('static/')[-1], _external=True),
    }

def handle_textual_exercise(exercise_type):
    """Handles the initialization of a textual exercise."""
    print("[handle_textual_exercise] Handling textual exercise.")

    exercise_data = generate_textual_exercise(exercise_type)
    if not exercise_data or "question" not in exercise_data:
        raise ValueError("Error generating textual exercise.")

    question = exercise_data.get("question", "")
    correct_answer = exercise_data.get("answer", "")

    print(f"[handle_textual_exercise] Generated question: {question}, Expected answer: {correct_answer}")

    global_state_manager.set_current_question({
        "expected_response": correct_answer,
        "question": question,
    })

    return {"message": f"Question: {question}", "image": None}

@chatbot_bp.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    user_message = data.get('message', '').strip().lower()
    print(f"[chatbot] Received user message: {user_message}")

    def evaluate_response_internal(user_message):
        try:
            current_question = global_state_manager.current_question
            if not current_question:
                return jsonify({"message": "Nessuna domanda attiva al momento."}), 400

            expected_response = current_question.get('expected_response', '').strip()

            # 🔴 Incrementiamo subito il numero di tentativi
            global_state_manager.increment_attempts()
            attempts = global_state_manager.attempts

            print(f"[DEBUG] Tentativi attuali: {attempts}")
            print(f"[DEBUG] Tipo di esercizio corrente: {global_state_manager.current_exercise}")

            # Valutiamo la risposta con l'LLM
            evaluation = evaluate_with_llm(user_message, expected_response)

            if evaluation.get("correct", False):
                feedback = f"✔️ Corretto! {evaluation.get('feedback', '')}"
                global_state_manager.reset_attempts()

                print("[evaluate_response_internal] Risposta corretta. Cercando prossima domanda...")

                next_question = global_state_manager.prepare_next_question()

                if next_question and "question" in next_question:
                    global_state_manager.set_current_question(next_question)
                    return jsonify({
                        "feedback": feedback,
                        "next_question": f"{next_question['question']}"
                    })

                print("[evaluate_response_internal] Nessuna domanda rimanente. Terminando esercizio.")
                global_state_manager.reset_current_exercise()
                return jsonify({
                    "feedback": feedback,
                    "message": "Hai completato l'esercizio! Se vuoi farne un altro, scegline uno nuovo dal menu."
                })

            if attempts < 3:
                print(f"[DEBUG] Tentativo {attempts}/3. Restando sulla stessa domanda.")
                return jsonify({
                    "feedback": f"❌ Errato. {evaluation.get('feedback', 'La risposta non è corretta.')}",
                    "tentativi": f"Tentativo {attempts}/3. Riprova."
                })

            # 🔴 Dopo il terzo errore, mostra la risposta corretta prima di passare alla prossima domanda
            feedback = f"❌ Hai esaurito i tentativi. La risposta corretta era: **{expected_response}**."
            print(f"[evaluate_response_internal] Tentativi esauriti. Mostrando la risposta corretta: {expected_response}")

            global_state_manager.reset_attempts()

            next_question = global_state_manager.prepare_next_question()

            if next_question and "question" in next_question:
                global_state_manager.set_current_question(next_question)
                return jsonify({
                    "feedback": feedback,
                    "next_question": f"Prossima domanda: {next_question['question']}",
                    "image": url_for('static', filename=next_question["image_url"].split('static/')[-1],
                                     _external=True) if next_question.get("image_url") else None
                })

            print(
                "[evaluate_response_internal] Nessuna domanda rimanente dopo tentativi esauriti. Terminando esercizio.")
            global_state_manager.reset_current_exercise()
            return jsonify({
                "feedback": feedback,
                "message": "L'esercizio è terminato. Vuoi sceglierne un altro?"
            })

        except Exception as e:
            print(f"[evaluate_response_internal] Errore: {e}")
            return jsonify({"message": "Errore nella valutazione della risposta.", "details": str(e)}), 500

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

