import unittest
from flask import Flask
from flaskr.models.database import db, create_user, get_user_by_id, update_user, delete_user, create_question, get_question_by_id, update_question, delete_question

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Set up a test Flask app and in-memory SQLite database
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)

        # Create the database and tables
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        # Clean up the database after each test
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_user(self):
        with self.app.app_context():
            user = create_user("testuser", "test@example.com", "hashedpassword")
            self.assertIsNotNone(user.id)
            self.assertEqual(user.username, "testuser")
            self.assertEqual(user.email, "test@example.com")

    def test_get_user_by_id(self):
        with self.app.app_context():
            user = create_user("testuser", "test@example.com", "hashedpassword")
            fetched_user = get_user_by_id(user.id)
            self.assertEqual(fetched_user.username, "testuser")

    def test_update_user(self):
        with self.app.app_context():
            user = create_user("testuser", "test@example.com", "hashedpassword")
            updated_user = update_user(user.id, username="updateduser")
            self.assertEqual(updated_user.username, "updateduser")

    def test_delete_user(self):
        with self.app.app_context():
            user = create_user("testuser", "test@example.com", "hashedpassword")
            delete_user(user.id)
            self.assertIsNone(get_user_by_id(user.id))

    def test_create_question(self):
        with self.app.app_context():
            question = create_question("What is Python?", "Easy", "Programming")
            self.assertIsNotNone(question.id)
            self.assertEqual(question.content, "What is Python?")
            self.assertEqual(question.difficulty, "Easy")

    def test_get_question_by_id(self):
        with self.app.app_context():
            question = create_question("What is Python?", "Easy", "Programming")
            fetched_question = get_question_by_id(question.id)
            self.assertEqual(fetched_question.content, "What is Python?")

    def test_update_question(self):
        with self.app.app_context():
            question = create_question("What is Python?", "Easy", "Programming")
            updated_question = update_question(question.id, content="What is Flask?")
            self.assertEqual(updated_question.content, "What is Flask?")

    def test_delete_question(self):
        with self.app.app_context():
            question = create_question("What is Python?", "Easy", "Programming")
            delete_question(question.id)
            self.assertIsNone(get_question_by_id(question.id))
