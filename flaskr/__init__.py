from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from .models.database import db
from .views import auth_bp  # Import the blueprint

def create_app():
    app = Flask(__name__)

    # Load environment variables from .env file
    load_dotenv(dotenv_path=".env") 

    # Debug: Print the loaded SQLALCHEMY_DATABASE_URI
    print("DEBUG: SQLALCHEMY_DATABASE_URI:", os.getenv('SQLALCHEMY_DATABASE_URI'))

    # Set configuration from environment variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    print("DEBUG: SQLAlchemy initialised:", db)
    migrate = Migrate(app, db)

    # Register blueprints
    app.register_blueprint(auth_bp)

    return app
