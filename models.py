from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    pin_hash = db.Column(db.String(255), nullable=False)
    # Relationship to platform passwords
    passwords = db.relationship('PlatformPassword', backref='user', lazy=True)

    def set_pin(self, pin):
        self.pin_hash = generate_password_hash(pin)

    def check_pin(self, pin):
        return check_password_hash(self.pin_hash, pin)

class PlatformPassword(db.Model):
    __tablename__ = 'passwords'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    platform = db.Column(db.String(100), nullable=False)
    encrypted_password = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=True, default='other')
    failed_attempts = db.Column(db.Integer, default=0)
    lock_until = db.Column(db.DateTime, nullable=True)

    def is_locked(self):
        if self.lock_until and datetime.utcnow() < self.lock_until:
            return True
        return False
