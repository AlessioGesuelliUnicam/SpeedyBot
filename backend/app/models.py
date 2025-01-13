from . import db
from datetime import datetime

class ExerciseWithImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(200), nullable=False)  # Percorso dell'immagine
    exercise_type_id = db.Column(db.Integer, db.ForeignKey('exercise_type.id'), nullable=False)  # Foreign key to ExerciseType
    description_it = db.Column(db.String(200), nullable=False)  # Descrizione in italiano
    description_en = db.Column(db.String(200), nullable=False)  # Descrizione in inglese
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)  # Data di caricamento

class ExerciseType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exerciseType = db.Column(db.String(100), nullable=False) # Tipologia di esercizio
    exerciseWithImage = db.Column(db.Boolean, default=False)  # Campo booleano
    prompt = db.Column(db.Text, nullable=False)  # Prompt associato
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)  # Data di caricamento