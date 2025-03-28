from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=True, server_default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime, nullable=True, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    quizzes = db.relationship('QuizResult', backref='user', lazy=True)

    def generate_log(self):
        db.session.add(Log(self.id))
        db.session.commit()

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    answers = db.relationship('Answer', backref='question', lazy=True)

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class QuizResult(db.Model):
    __tablename__ = 'quiz_results'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Integer, nullable=False)  # in seconds
    completed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Leaderboard(db.Model):
    __tablename__ = 'leaderboards'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_score = db.Column(db.Integer, nullable=False, default=0)
    quizzes_completed = db.Column(db.Integer, nullable=False, default=0)
    average_time = db.Column(db.Float, nullable=False, default=0)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# configure a log class
class Log(db.Model):
    __tablename__ = 'logs'

    user = db.relationship("User", back_populates="log")

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    registration = db.Column(db.DateTime, nullable=False)
    latest_login = db.Column(db.DateTime, default=None)
    previous_login = db.Column(db.DateTime, default=None)

    def __init__(self, userid):
        self.userid = userid
        self.registration = datetime.now()

# View classes
class UserView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = (
        'id', 'username', 'email', 'password_hash', 'phone_number', 'location', 'created_at', 'last_login', 'quizzes')

class QuestionView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = (
        'id', 'content', 'difficulty', 'topic', 'created_at', 'answers')

class AnswerView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = (
        'id', 'question_id', 'content', 'is_correct', 'created_at')

class ResultView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = (
        'id', 'user_id', 'score', 'time_taken', 'completed_at')

class LeaderboardView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = (
        'id', 'user_id', 'total_score', 'quizzes_completed', 'average_time', 'last_updated')
