import json
from flask import Blueprint, request, jsonify, current_app
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
def upload_file():
    file = request.files.get('file')
    exercise_type_id = request.form.get('exercise_type')
    description_it = request.form.get('description_it')
    description_en = request.form.get('description_en')

    if not all([file, exercise_type_id, description_it, description_en]):
        return jsonify({"error": "Missing data."}), 400

    exercise_type_id = int(exercise_type_id)
    subfolder = 'animals' if exercise_type_id == 1 else 'signals' if exercise_type_id == 2 else None
    if not subfolder:
        return jsonify({"error": "Invalid exercise_type_id."}), 400

    # Creazione di un nome file sicuro con timestamp
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    filename = f"{timestamp}_{secure_filename(file.filename)}"

    # Definizione del percorso della cartella di upload
    upload_folder = Path(current_app.config['UPLOAD_FOLDER']) / subfolder
    upload_folder.mkdir(parents=True, exist_ok=True)  # Crea la cartella se non esiste

    filepath = upload_folder / filename  # Percorso completo del file
    file.save(filepath)  # Salva il file

    # Salva il percorso relativo nel database
    file_path = filepath.relative_to(current_app.root_path)

    new_entry = ExerciseWithImage(
        file_path=str(file_path),  # Converte in stringa per il database
        exercise_type_id=exercise_type_id,
        description_it=description_it,
        description_en=description_en,
        upload_date=datetime.utcnow()
    )
    db.session.add(new_entry)
    db.session.commit()

    print(f"✅ File salvato in: {filepath}")
    print(f"✅ Percorso salvato nel database: {file_path}")

    return jsonify({"message": "File uploaded successfully"}), 201

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