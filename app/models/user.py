from app.utils import db  # Import db from your utils (or wherever it's defined)
from sqlalchemy import Column, String

class User(db.Model):
    __tablename__ = "users"
    id = Column(db.Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    phone_number = Column(String(15), nullable=False, unique=True)
    password = Column(String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")

    def __repr__(self):
        return f"<User {self.username}>"

# Define the MedicalRecord model
class MedicalRecord(db.Model):
    __tablename__ = "medical_records"
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(20))
    age = db.Column(db.Integer)
    hypertension = db.Column(db.Integer)
    ever_married = db.Column(db.String(20))
    work_type = db.Column(db.String(50))
    Residence_type = db.Column(db.String(50))
    avg_glucose_level = db.Column(db.Float)
    bmi = db.Column(db.Float)
    smoking_status = db.Column(db.String(50))
    stroke_risk = db.Column(db.String(50))
    prediction = db.Column(db.String(50))
