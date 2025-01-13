from flask import Blueprint, request, jsonify
from app.models import ExerciseType
from app import db
from datetime import datetime

exercise_type_bp = Blueprint('exercise_type', __name__)

@exercise_type_bp.route('/api/exercise-types', methods=['POST'])
def create_exercise_type():
    data = request.get_json()
    exercise_type = data.get('exerciseType')
    exercise_with_image = data.get('exerciseWithImage', False)
    prompt = data.get('prompt')  # Aggiunto per il prompt

    if not exercise_type:
        return jsonify({'error': 'exerciseType is required'}), 400

    if not prompt:
        return jsonify({'error': 'prompt is required'}), 400

    new_exercise_type = ExerciseType(
        exerciseType=exercise_type,
        exerciseWithImage=exercise_with_image,
        prompt=prompt  # Associa il valore del prompt
    )
    db.session.add(new_exercise_type)
    db.session.commit()

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

    db.session.delete(exercise_type)
    db.session.commit()
    return jsonify({'message': 'ExerciseType deleted successfully'}), 200

