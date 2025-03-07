from config import app, db
from sqlalchemy import text

def test_database_connection():
    with app.app_context():
        db.session.execute(text('SELECT 1'))