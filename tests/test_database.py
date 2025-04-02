import pytest
from sqlalchemy import text
from config import app
from models.database import db, create_user, get_user_by_id, update_user, delete_user, create_question, get_question_by_id, update_question, delete_question

def test_database_connection():
    with app.app_context():
        db.session.execute(text('SELECT 1'))

@pytest.fixture()
def database_context():
    with app.app_context():
        # Create the database and tables
        db.create_all()

        yield app.app_context()

        # Clean up the database after each test
        db.session.remove()
        db.drop_all()

def test_create_user(database_context):
    with database_context:
        user = create_user("testuser", "test@example.com", "hashedpassword")
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"

def test_get_user_by_id(database_context):
    with database_context:
        user = create_user("testuser", "test@example.com", "hashedpassword")
        fetched_user = get_user_by_id(user.id)
        assert fetched_user.username == "testuser"

def test_update_user(database_context):
    with database_context:
        user = create_user("testuser", "test@example.com", "hashedpassword")
        updated_user = update_user(user.id, username="updateduser")
        assert updated_user.username == "updateduser"

def test_delete_user(database_context):
    with database_context:
        user = create_user("testuser", "test@example.com", "hashedpassword")
        delete_user(user.id)
        assert get_user_by_id(user.id) is None

def test_create_question(database_context):
    with database_context:
        question = create_question("What is Python?", "Easy", "Programming")
        assert question.id is not None
        assert question.content == "What is Python?"
        assert question.difficulty == "Easy"

def test_get_question_by_id(database_context):
    with database_context:
        question = create_question("What is Python?", "Easy", "Programming")
        fetched_question = get_question_by_id(question.id)
        assert fetched_question.content == "What is Python?"

def test_update_question(database_context):
    with database_context:
        question = create_question("What is Python?", "Easy", "Programming")
        updated_question = update_question(question.id, content="What is Flask?")
        assert updated_question.content == "What is Flask?"

def test_delete_question(database_context):
    with database_context:
        question = create_question("What is Python?", "Easy", "Programming")
        delete_question(question.id)
        assert get_question_by_id(question.id) is None