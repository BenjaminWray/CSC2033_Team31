from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .models.database import db

def create_app():
    app = Flask(__name__)
    
    # Explicitly load environment variables
    from dotenv import load_dotenv
    import os
    load_dotenv()

    # Configure the app
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)

    # Define a route for the root URL
    @app.route('/')
    def index():
        return "Welcome to the Quiz System!"

    return app
