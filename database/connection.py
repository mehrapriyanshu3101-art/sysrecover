from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        # Drop all tables and recreate for development
        db.drop_all()
        db.create_all()
