import json
import os

from flask import Blueprint, request, jsonify, current_app, url_for
from werkzeug.utils import secure_filename
from pathlib import Path
from app.models import ExerciseWithImage, ExerciseType
from app import db
from datetime import datetime

upload_bp = Blueprint('upload', __name__)

# Ottenere i tipi di esercizi con immagini
@upload_bp.route('/exercise-types-with-image', methods=['GET'])
def get_exercise_types_with_image():
    try:
        exercise_types = ExerciseType.query.filter_by(exerciseWithImage=True).all()
        exercise_types_data = [{'id': et.id, 'exerciseType': et.exerciseType} for et in exercise_types]
        return jsonify(exercise_types_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Upload di un'immagine per un esercizio
@upload_bp.route('/upload-image-exercise', methods=['POST'])
def upload_image_exercise():
    """
    Upload a new image-based exercise with cross-platform support.
    """
    try:
        file = request.files.get('file')
        exercise_type_id = request.form.get('exercise_type')
        description_it = request.form.get('description_it')
        description_en = request.form.get('description_en')

        if not all([file, exercise_type_id, description_it, description_en]):
            return jsonify({"error": "Missing data. Please provide file, exercise_type, description_it, and description_en."}), 400

        exercise_type_id = int(exercise_type_id)

        # Recupera il nome dell'esercizio dal database
        exercise = ExerciseType.query.get(exercise_type_id)
        if not exercise:
            return jsonify({"error": "Exercise type not found."}), 404

        # Normalizza il nome della cartella (percorso dinamico)
        exercise_folder = exercise.exerciseType.lower().replace(" ", "_")
        upload_folder = os.path.join(current_app.root_path, "static", "uploads", exercise_folder)
        os.makedirs(upload_folder, exist_ok=True)  # Crea la cartella se non esiste

        # Genera il nome del file con timestamp per evitare sovrascritture
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{secure_filename(file.filename)}"

        # Percorso assoluto dove salvare il file
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # ✅ Costruiamo direttamente il percorso relativo in formato UNIX
        relative_path = f"static/uploads/{exercise_folder}/{filename}"

        print(f"✅ [DEBUG] Percorso salvato nel DB: {relative_path}")  # Debug

        # Salva nel database
        new_entry = ExerciseWithImage(
            file_path=relative_path,  # Percorso già corretto
            exercise_type_id=exercise_type_id,
            description_it=description_it,
            description_en=description_en,
            upload_date=datetime.utcnow()
        )
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({
            "message": "File uploaded successfully.",
            "file_url": url_for('static', filename=relative_path, _external=True)
        }), 201

    except Exception as e:
        print(f"[upload_image_exercise] Error: {e}")
        return jsonify({"error": "Failed to upload image exercise.", "details": str(e)}), 500

# Upload di un esercizio testuale
@upload_bp.route('/upload-text-exercise', methods=['POST'])
def upload_text_exercise():
    exercise_type_id = request.json.get('exercise_type_id')
    question = request.json.get('question')
    answer = request.json.get('answer')

    if not all([exercise_type_id, question, answer]):
        return jsonify({"error": "Missing required fields"}), 400

    # Recupera l'exerciseType dal database
    exercise_type_record = ExerciseType.query.get(exercise_type_id)
    if not exercise_type_record:
        return jsonify({"error": "Invalid exercise type ID"}), 404

    # Normalizza il nome del file
    exercise_type = exercise_type_record.exerciseType.lower().replace(' ', '_')

    # Percorso corretto e compatibile
    exercises_dir = Path(current_app.root_path) / 'static' / 'exercises'
    exercises_dir.mkdir(parents=True, exist_ok=True)  # Assicura che la cartella esista

    file_path = exercises_dir / f"{exercise_type}.json"

    # Creazione del file JSON se non esiste
    if not file_path.exists():
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump({exercise_type: []}, file)

    # Lettura del contenuto esistente
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Aggiunta della nuova domanda
    data[exercise_type].append({"question": question, "solution": answer})

    # Salvataggio del file aggiornato
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print(f"✅ Esercizio testuale salvato in: {file_path}")

    return jsonify({"message": "Text exercise added successfully"}), 201

# Ottenere i tipi di esercizi senza immagini
@upload_bp.route('/exercise-types-no-image', methods=['GET'])
def get_exercise_types_no_image():
    try:
        exercise_types = ExerciseType.query.filter_by(exerciseWithImage=False).all()
        exercise_types_data = [{'id': et.id, 'exerciseType': et.exerciseType} for et in exercise_types]
        return jsonify(exercise_types_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500