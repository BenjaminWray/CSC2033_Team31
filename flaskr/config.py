from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost:3306/database'

db = SQLAlchemy(app)
migrate = Migrate(app, db)