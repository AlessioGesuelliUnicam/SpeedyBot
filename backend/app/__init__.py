from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask import request
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}},
         supports_credentials=True,
         methods=["GET", "POST", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"])

    @app.before_request
    def handle_options():
        if request.method == "OPTIONS":
            response = app.make_response("")  # Risposta vuota
            response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
            response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
            return response

    # Configura il database
    app.config.from_object('config.Config')

    # Configura la cartella degli upload
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'app/static/uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Inizializza le estensioni
    db.init_app(app)
    migrate.init_app(app, db)

    # Registra i blueprint delle rotte
    from app.routes.upload import upload_bp
    from app.chatbot import chatbot_bp  # Importa il blueprint del chatbot
    from app.routes.exercise_type import exercise_type_bp # Importa il blueprint del tipo di esercizio

    app.register_blueprint(upload_bp)
    app.register_blueprint(chatbot_bp)  # Registra il blueprint del chatbot
    app.register_blueprint(exercise_type_bp)  # Registra il blueprint del tipo di esercizio

    # Route per servire i file dalla cartella uploads
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app