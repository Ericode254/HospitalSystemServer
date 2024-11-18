from werkzeug.security import generate_password_hash
from app.models import User
from app.utils import db

def create_user(data):
    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        user_name=data['user_name'],
        phone_number=data['phone_number'],
        email=data['email'],
        password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    return {
        "id": new_user.id,
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "user_name": new_user.user_name,
        "phone_number": new_user.phone_number,
        "email": new_user.email
    }

