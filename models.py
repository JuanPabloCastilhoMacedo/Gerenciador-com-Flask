from datetime import datetime, timedelta, timezone
from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="pendente")

class User(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)

class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    token = db.Column(db.String(128), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, hours_valid=1):
        self.user_id = user_id
        self.token = str(uuid.uuid4())
        self.expires_at = datetime.now(timezone.utc) + timedelta(hours=hours_valid)

    def is_expired(self):
        return datetime.now(timezone.utc) > self.expires_at