import os
import json
from flask import url_for, current_app, jsonify, Blueprint, request
from werkzeug.utils import secure_filename
from app.models import ExerciseType, ExerciseWithImage
from app import db
from datetime import datetime

materials_bp = Blueprint('materials', __name__)

@materials_bp.route('/materials-with-images', methods=['GET'])
def get_materials_with_images():
    """
    Fetch all uploaded materials with images grouped by exercise type.
    """
    try:
        materials = []

        # Fetch exercise types from the database
        exercise_types = ExerciseType.query.filter_by(exerciseWithImage=True).all()
        for exercise_type in exercise_types:
            # Query for image-based materials
            files = ExerciseWithImage.query.filter_by(exercise_type_id=exercise_type.id).all()
            materials.append({
                "id": exercise_type.id,  # Aggiungi l'ID del tipo di esercizio
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

        return jsonify({"materials": materials})

    except Exception as e:
        print(f"[get_materials_with_images] Error: {e}")
        return jsonify({"error": "Failed to fetch materials."}), 500


@materials_bp.route('/upload-image-exercise', methods=['POST'])
def upload_image_exercise():
    """
    Upload a new image-based exercise.
    """
    file = request.files.get('file')
    exercise_type_id = request.form.get('exercise_type')  # Exercise type ID
    description_it = request.form.get('description_it')  # Description in Italian
    description_en = request.form.get('description_en')  # Description in English

    if not all([file, exercise_type_id, description_it, description_en]):
        return jsonify({"error": "Missing data. Please provide file, exercise_type, description_it, and description_en."}), 400

    exercise_type_id = int(exercise_type_id)
    subfolder = 'uploads'  # Default subfolder
    filename = secure_filename(file.filename)
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    filepath = os.path.join(upload_folder, filename)
    os.makedirs(upload_folder, exist_ok=True)
    file.save(filepath)

    # Save the data to the database
    new_entry = ExerciseWithImage(
        file_path=filepath,
        exercise_type_id=exercise_type_id,
        description_it=description_it,
        description_en=description_en,
        upload_date=datetime.utcnow()
    )
    db.session.add(new_entry)
    db.session.commit()

    return jsonify({"message": "File uploaded successfully"}), 201

@materials_bp.route('/materials/<int:material_id>', methods=['DELETE'])
def delete_material(material_id):
    """
    Delete a specific material (image) by its ID.
    """
    try:
        # Recupera il materiale dal database
        material = ExerciseWithImage.query.get(material_id)
        if not material:
            print(f"[delete_material] Material with ID {material_id} not found.")
            return jsonify({"error": "Material not found"}), 404

        # Percorso completo dell'immagine
        file_path = os.path.join(current_app.root_path, 'static', material.file_path)

        # Rimuovi il file dal filesystem
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"[delete_material] Deleted file: {file_path}")
        else:
            print(f"[delete_material] File not found: {file_path}")

        # Elimina il record dal database
        db.session.delete(material)
        db.session.commit()
        print(f"[delete_material] Deleted record for material ID {material_id}.")

        return jsonify({"message": "Material deleted successfully."}), 200
    except Exception as e:
        print(f"[delete_material] Error: {e}")
        return jsonify({"error": "Failed to delete material.", "details": str(e)}), 500