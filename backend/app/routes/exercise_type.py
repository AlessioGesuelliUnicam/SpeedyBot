import json
import os

from flask import Blueprint, request, jsonify, current_app
from app.models import ExerciseType, ExerciseWithImage
from app import db
from datetime import datetime

exercise_type_bp = Blueprint('exercise_type', __name__)

@exercise_type_bp.route('/api/exercise-types', methods=['POST'])
def create_exercise_type():
    data = request.get_json()
    exercise_type = data.get('exerciseType')
    exercise_with_image = data.get('exerciseWithImage', False)
    prompt = data.get('prompt', "")  # Valore di default: stringa vuota

    if not exercise_type:
        return jsonify({'error': 'exerciseType is required'}), 400

    # Crea un nuovo record nel database
    new_exercise_type = ExerciseType(
        exerciseType=exercise_type,
        exerciseWithImage=exercise_with_image,
        prompt=prompt  # Usa il valore fornito o il default ""
    )
    db.session.add(new_exercise_type)
    db.session.commit()

    # Trasforma l'exerciseType in un nome di file
    exercise_type_filename = exercise_type.lower().replace(' ', '_')
    file_path = os.path.join(current_app.root_path, 'static', 'exercises', f"{exercise_type_filename}.json")

    # Crea la directory se non esiste
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Controlla se il file esiste, altrimenti lo crea
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump({exercise_type_filename: []}, file)

    return jsonify({'message': 'ExerciseType created successfully'}), 201


@exercise_type_bp.route('/api/exercise-types', methods=['GET'])
def get_exercise_types():
    exercise_types = ExerciseType.query.all()
    result = [
        {
            'id': et.id,
            'exerciseType': et.exerciseType,
            'exerciseWithImage': et.exerciseWithImage,
            'prompt': et.prompt,
            'upload_date': et.upload_date.isoformat()
        } for et in exercise_types
    ]
    return jsonify(result), 200


@exercise_type_bp.route('/api/exercise-types/<int:id>', methods=['GET'])
def get_exercise_type(id):
    exercise_type = ExerciseType.query.get(id)
    if not exercise_type:
        return jsonify({'error': 'ExerciseType not found'}), 404

    result = {
        'id': exercise_type.id,
        'exerciseType': exercise_type.exerciseType,
        'exerciseWithImage': exercise_type.exerciseWithImage,
        'prompt': exercise_type.prompt,
        'upload_date': exercise_type.upload_date.isoformat()
    }
    return jsonify(result), 200


@exercise_type_bp.route('/api/exercise-types/<int:id>', methods=['PUT'])
def update_exercise_type(id):
    exercise_type = ExerciseType.query.get(id)
    if not exercise_type:
        return jsonify({'error': 'ExerciseType not found'}), 404

    data = request.get_json()
    exercise_type.exerciseType = data.get('exerciseType', exercise_type.exerciseType)
    exercise_type.exerciseWithImage = data.get('exerciseWithImage', exercise_type.exerciseWithImage)

    db.session.commit()
    return jsonify({'message': 'ExerciseType updated successfully'}), 200


@exercise_type_bp.route('/api/exercise-types/<int:id>', methods=['DELETE'])
def delete_exercise_type(id):
    exercise_type = ExerciseType.query.get(id)
    if not exercise_type:
        return jsonify({'error': 'ExerciseType not found'}), 404

    try:
        # Rimuovi il file JSON collegato
        exercise_type_filename = exercise_type.exerciseType.lower().replace(' ', '_')
        json_file_path = os.path.join(current_app.root_path, 'static', 'exercises', f"{exercise_type_filename}.json")
        if os.path.exists(json_file_path):
            os.remove(json_file_path)

        # Rimuovi i file immagine collegati, se esistono
        if exercise_type.exerciseWithImage:
            image_records = ExerciseWithImage.query.filter_by(exercise_type_id=id).all()
            for image_record in image_records:
                image_path = os.path.join(current_app.root_path, 'static', image_record.file_path)
                if os.path.exists(image_path):
                    os.remove(image_path)
                db.session.delete(image_record)  # Rimuovi il record dal database

        # Elimina l'esercizio dal database
        db.session.delete(exercise_type)
        db.session.commit()

        return jsonify({'message': 'ExerciseType and related files deleted successfully'}), 200
    except Exception as e:
        print(f"[delete_exercise_type] Error: {e}")
        return jsonify({'error': 'An error occurred while deleting the exercise type and files.'}), 500

