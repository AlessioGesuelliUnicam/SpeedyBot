import json
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from app.models import ExerciseWithImage, ExerciseType
from app import db
from datetime import datetime

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/exercise-types-with-image', methods=['GET'])
def get_exercise_types_with_image():
    try:
        # Query al database per ottenere gli exercise_type con exerciseWithImage=True
        exercise_types = ExerciseType.query.filter_by(exerciseWithImage=True).all()
        exercise_types_data = [{'id': et.id, 'exerciseType': et.exerciseType} for et in exercise_types]
        return jsonify(exercise_types_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@upload_bp.route('/upload-image-exercise', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    exercise_type_id = request.form.get('exercise_type')  # Ottieni l'ID dell'exerciseType
    description_it = request.form.get('description_it')  # Descrizione in italiano
    description_en = request.form.get('description_en')  # Descrizione in inglese

    if not all([file, exercise_type_id, description_it, description_en]):
        return jsonify({"error": "Missing data. Please provide file, exercise_type, description_it, and description_en."}), 400

    exercise_type_id = int(exercise_type_id)
    if exercise_type_id == 1:
        subfolder = 'animals'
    elif exercise_type_id == 2:
        subfolder = 'signals'
    else:
        return jsonify({"error": "Invalid exercise_type_id."}), 400

    filename = secure_filename(file.filename)
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    filepath = os.path.join(upload_folder, filename)
    os.makedirs(upload_folder, exist_ok=True)
    file.save(filepath)

    new_entry = ExerciseWithImage(
        file_path=filepath,
        exercise_type_id=exercise_type_id,  # Salva l'ID dell'esercizio
        description_it=description_it,
        description_en=description_en,
        upload_date=datetime.utcnow()
    )
    db.session.add(new_entry)
    db.session.commit()

    return jsonify({"message": "File uploaded successfully"}), 201

@upload_bp.route('/upload-text-exercise', methods=['POST'])
def upload_text_exercise():
    exercise_type_id = request.json.get('exercise_type_id')
    question = request.json.get('question')
    answer = request.json.get('answer')

    # Controlla che tutti i dati richiesti siano presenti
    if not all([exercise_type_id, question, answer]):
        return jsonify({"error": "Missing required fields"}), 400

    # Recupera l'exerciseType dal database usando l'ID fornito
    exercise_type_record = ExerciseType.query.get(exercise_type_id)
    if not exercise_type_record:
        return jsonify({"error": "Invalid exercise type ID"}), 404

    # Trasforma l'exerciseType in formato file
    exercise_type = exercise_type_record.exerciseType.lower().replace(' ', '_')
    file_path = os.path.join(current_app.root_path, 'static', 'exercises', f"{exercise_type}.json")

    # Crea la directory se non esiste
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Controlla se il file esiste, altrimenti lo crea
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump({exercise_type: []}, file)

    # Carica il contenuto del file esistente
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Aggiunge la nuova domanda e risposta
    data[exercise_type].append({
        "question": question,
        "solution": answer
    })

    # Salva le modifiche al file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    return jsonify({"message": "Text exercise added successfully"}), 201

@upload_bp.route('/exercise-types-no-image', methods=['GET'])
def get_exercise_types_no_image():
    try:
        # Query per ottenere gli exerciseType con exerciseWithImage=False
        exercise_types = ExerciseType.query.filter_by(exerciseWithImage=False).all()
        exercise_types_data = [{'id': et.id, 'exerciseType': et.exerciseType} for et in exercise_types]
        return jsonify(exercise_types_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500