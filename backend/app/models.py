from . import db
from datetime import datetime

class ExerciseWithImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(200), nullable=False)  # Image file path
    exercise_type_id = db.Column(db.Integer, db.ForeignKey('exercise_type.id'), nullable=False)  # Foreign key to ExerciseType
    description_it = db.Column(db.String(200), nullable=False)  # Description in Italian
    description_en = db.Column(db.String(200), nullable=False)  # Description in English
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)  # Upload date

class ExerciseType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exerciseType = db.Column(db.String(100), nullable=False)  # Exercise type
    exerciseWithImage = db.Column(db.Boolean, default=False)  # Boolean field
    prompt = db.Column(db.Text, nullable=False)  # Associated prompt for implementing text-based exercises with LLM
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)  # Upload date