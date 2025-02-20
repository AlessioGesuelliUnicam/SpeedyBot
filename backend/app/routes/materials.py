import os
import json
from flask import url_for, current_app, jsonify, Blueprint, request
from werkzeug.utils import secure_filename
from app.models import ExerciseType, ExerciseWithImage
from app import db
from datetime import datetime
from pathlib import Path

materials_bp = Blueprint('materials', __name__)

# === Metodi per gli esercizi con immagini ===
@materials_bp.route('/materials-with-images', methods=['GET'])
def get_materials_with_images():
    """
    Fetch all uploaded materials with images grouped by exercise type.
    """
    try:
        materials = []
        exercise_types = ExerciseType.query.filter_by(exerciseWithImage=True).all()

        for exercise_type in exercise_types:
            files = ExerciseWithImage.query.filter_by(exercise_type_id=exercise_type.id).all()
            materials.append({
                "id": exercise_type.id,
                "exerciseType": exercise_type.exerciseType,
                "materials": [
                    {
                        "id": file.id,
                        "filePath": url_for('static', filename=file.file_path.split('static/')[-1], _external=True),
                        "descriptionIt": file.description_it,
                        "descriptionEn": file.description_en
                    }
                    for file in files
                ]
            })

        return jsonify({"materials": materials}), 200

    except Exception as e:
        print(f"[get_materials_with_images] Error: {e}")
        return jsonify({"error": "Failed to fetch materials."}), 500


@materials_bp.route('/upload-image-exercise', methods=['POST'])
def upload_image_exercise():
    """
    Upload a new image-based exercise with dynamic folder handling.
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

        exercise_folder = exercise.exerciseType.lower().replace(" ", "_")  # Normalizza il nome della cartella
        upload_folder = Path(current_app.root_path) / "static" / "uploads" / exercise_folder
        upload_folder.mkdir(parents=True, exist_ok=True)  # Crea la cartella se non esiste

        # Salva il file in modo sicuro
        filename = secure_filename(file.filename)
        file_path = upload_folder / filename
        file.save(file_path)

        # Salva il percorso nel database (in formato UNIX per compatibilità)
        new_entry = ExerciseWithImage(
            file_path=file_path.relative_to(Path(current_app.root_path) / "static").as_posix(),
            exercise_type_id=exercise_type_id,
            description_it=description_it,
            description_en=description_en,
            upload_date=datetime.utcnow()
        )
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"message": "File uploaded successfully."}), 201

    except Exception as e:
        print(f"[upload_image_exercise] Error: {e}")
        return jsonify({"error": "Failed to upload image exercise."}), 500


@materials_bp.route('/materials/<int:material_id>', methods=['DELETE'])
def delete_material(material_id):
    """
    Delete a specific material (image) by its ID.
    """
    try:
        material = ExerciseWithImage.query.get(material_id)
        if not material:
            return jsonify({"error": "Material not found"}), 404

        file_path = os.path.join(current_app.root_path, 'static', material.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.delete(material)
        db.session.commit()

        return jsonify({"message": "Material deleted successfully."}), 200

    except Exception as e:
        print(f"[delete_material] Error: {e}")
        return jsonify({"error": "Failed to delete material.", "details": str(e)}), 500


# === Metodi per gli esercizi testuali ===
@materials_bp.route('/materials-text', methods=['GET'])
def get_textual_materials():
    """
    Fetch all textual materials grouped by exercise type.
    """
    try:
        materials = []
        exercises_path = os.path.join(current_app.root_path, 'static', 'exercises')

        if not os.path.exists(exercises_path):
            return jsonify({"materials": []}), 200

        for file_name in os.listdir(exercises_path):
            if file_name.endswith('.json'):
                file_path = os.path.join(exercises_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    materials.append({
                        "fileName": file_name,
                        "exercises": data
                    })

        return jsonify({"materials": materials}), 200

    except Exception as e:
        print(f"[get_textual_materials] Error: {e}")
        return jsonify({"error": "Failed to fetch textual materials."}), 500


@materials_bp.route('/materials-text', methods=['POST'])
def upload_textual_material():
    """
    Upload a new textual exercise file (JSON).
    """
    try:
        file = request.files.get('file')
        if not file or not file.filename.endswith('.json'):
            return jsonify({"error": "Invalid file type. Only JSON files are allowed."}), 400

        exercises_path = os.path.join(current_app.root_path, 'static', 'exercises')
        os.makedirs(exercises_path, exist_ok=True)

        filename = secure_filename(file.filename)
        file.save(os.path.join(exercises_path, filename))

        return jsonify({"message": "File uploaded successfully."}), 201

    except Exception as e:
        print(f"[upload_textual_material] Error: {e}")
        return jsonify({"error": "Failed to upload textual material."}), 500


@materials_bp.route('/materials-text/<file_name>', methods=['DELETE'])
def delete_textual_material(file_name):
    """
    Delete a textual exercise file (JSON).
    """
    try:
        exercises_path = os.path.join(current_app.root_path, 'static', 'exercises', file_name)
        if os.path.exists(exercises_path):
            os.remove(exercises_path)
            return jsonify({"message": "File deleted successfully."}), 200
        else:
            return jsonify({"error": "File not found."}), 404

    except Exception as e:
        print(f"[delete_textual_material] Error: {e}")
        return jsonify({"error": "Failed to delete textual material."}), 500


@materials_bp.route('/materials-text/<file_name>', methods=['PUT'])
def update_textual_material(file_name):
    try:
        print(f"Updating file: {file_name}")  # Debug: stampa il nome del file
        exercises_path = os.path.join(current_app.root_path, 'static', 'exercises', file_name)
        print(f"Resolved path: {exercises_path}")  # Debug: stampa il percorso del file

        # Controlla se il file esiste
        if not os.path.exists(exercises_path):
            return jsonify({"error": "File not found"}), 404

        data = request.get_json()
        print(f"Received data: {data}")  # Debug: stampa i dati ricevuti

        # Salva il contenuto JSON nel file
        with open(exercises_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return jsonify({"message": "File updated successfully."}), 200
    except Exception as e:
        print(f"[update_textual_material] Error: {e}")  # Stampa l'errore
        return jsonify({"error": "Failed to update file.", "details": str(e)}), 500