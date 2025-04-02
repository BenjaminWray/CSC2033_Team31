from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate 
from .models.database import db 
 
def create_app(): 
    app = Flask(__name__) 
    app.config.from_prefixed_env() 
    db.init_app(app) 
    migrate = Migrate(app, db) 
    return app 
