from app.utils import db  # Import db from your utils (or wherever it's defined)
from sqlalchemy import Column, String

class User(db.Model):
    id = Column(db.Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    phone_number = Column(String(15), nullable=False, unique=True)
    password = Column(String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")

    def __repr__(self):
        return f"<User {self.username}>"

