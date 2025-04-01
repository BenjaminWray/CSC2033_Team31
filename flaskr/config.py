import os
from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# load environment variables from .env file
load_dotenv()

# get database connection info from environment variables
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = os.getenv('MYSQL_PORT')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

# configure database
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# configure a question Class
class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, nullable=False)

    def __init__(self, question_text, answer_text):
        self.question_text = question_text
        self.answer_text = answer_text
        self.created = datetime.now()

    def update(self, new_question, new_answer):
        self.question_text = new_question
        self.answer_text = new_answer


# configure a user class
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='end_user')
    time_joined = db.Column(db.DateTime, nullable=False)

    def __init__(self, email, password, firstname, lastname):
        self.email = email
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.time_joined = datetime.now()

    def generate_log(self):
        db.session.add(Log(self.id))
        db.session.commit()

# configure a log class
class Log(db.Model):
    __tablename__ = 'logs'

    user = db.relationship("User", back_populates="log")

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    registration = db.Column(db.DateTime, nullable=False)
    latestlogin = db.Column(db.DateTime, default=None)
    previouslogin = db.Column(db.DateTime, default=None)

    def __init__(self, userid):
        self.userid = userid
        self.registration = datetime.now()