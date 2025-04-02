from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timezone
from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy()
migrate = Migrate()

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

    # Add the relationship between log and user
    # This is a one-to-one relationship
    log = db.relationship("Log", back_populates="user", uselist=False)

    def generate_log(self):
        db.session.add(Log(self.id))
        db.session.commit()

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    answers = db.relationship('Answer', backref='question', lazy=True)

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))

class QuizResult(db.Model):
    __tablename__ = 'quiz_results'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Integer, nullable=False)  # in seconds
    completed_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))

class Leaderboard(db.Model):
    __tablename__ = 'leaderboards'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_score = db.Column(db.Integer, nullable=False, default=0)
    quizzes_completed = db.Column(db.Integer, nullable=False, default=0)
    average_time = db.Column(db.Float, nullable=False, default=0)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))

#configure a log class
class Log(db.Model):
    __tablename__ = 'logs'

    user = db.relationship("User", back_populates="log")

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
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
        'id', 'userid', 'score', 'time_taken', 'completed_at')

class LeaderboardView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = (
        'id', 'userid', 'total_score', 'quizzes_completed', 'average_time', 'last_updated')

# CRUD operations for Questions
def create_question(content, difficulty, topic):
    question = Question(content=content, difficulty=difficulty, topic=topic)
    db.session.add(question)
    db.session.commit()
    return question

def get_question_by_id(question_id):
    return db.session.get(Question, question_id)

def update_question(question_id, content=None, difficulty=None, topic=None):
    question = db.session.get(Question, question_id)
    if question:
        if content:
            question.content = content
        if difficulty:
            question.difficulty = difficulty
        if topic:
            question.topic = topic
        db.session.commit()
    return question

def delete_question(question_id):
    question = db.session.get(Question, question_id)
    if question:
        db.session.delete(question)
        db.session.commit()
    return question

# CRUD operations for Answers
def create_answer(question_id, content, is_correct=False):
    answer = Answer(question_id=question_id, content=content, is_correct=is_correct)
    db.session.add(answer)
    db.session.commit()
    return answer

def get_answers_by_question_id(question_id):
    return Answer.query.filter_by(question_id=question_id).all()

def update_answer(answer_id, content=None, is_correct=None):
    answer = db.session.get(Answer, answer_id)
    if answer:
        if content:
            answer.content = content
        if is_correct is not None:
            answer.is_correct = is_correct
        db.session.commit()
    return answer

def delete_answer(answer_id):
    answer = db.session.get(Answer, answer_id)
    if answer:
        db.session.delete(answer)
        db.session.commit()
    return answer

# CRUD operations for User
def create_user(username, email, password_hash, phone_number=None, location=None):
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        phone_number=phone_number,
        location=location
    )
    db.session.add(user)
    db.session.commit()
    return user

def get_user_by_id(user_id):
    return db.session.get(User, user_id)

def update_user(user_id, username=None, email=None, phone_number=None, location=None):
    user = db.session.get(User, user_id)
    if user:
        if username:
            user.username = username
        if email:
            user.email = email
        if phone_number:
            user.phone_number = phone_number
        if location:
            user.location = location
        db.session.commit()
    return user

def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return user
