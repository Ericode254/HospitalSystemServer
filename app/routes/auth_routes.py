from flask import Blueprint, request, jsonify, make_response
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import datetime
from app.models import User
from functools import wraps
import os
from app.utils import db
from sqlalchemy.exc import IntegrityError
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from app.utils import mail

auth_bp = Blueprint('auth', __name__)

# Initialize the serializer with the secret key
s = URLSafeTimedSerializer(os.getenv("SECRET_KEY", "testing"))

# Secret key for JWT encoding/decoding
SECRET_KEY = os.getenv("SECRET_KEY", "testing") 
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable not set!")

# Helper function to check for token and role authorization
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({"error": "Token is missing!"}), 403

        try:
            # Decode the token to get the user info
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({"error": "User not found"}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 403
        except Exception as e:
            return jsonify({"error": "Token validation error", "details": str(e)}), 403

        # Add user to request context
        request.current_user = current_user
        return f(*args, **kwargs)

    return decorated_function

# Role-based access decorator
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not hasattr(request, 'current_user') or request.current_user.role not in roles:
                return jsonify({"error": "Permission denied!"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

@auth_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()  # Get the data sent from the frontend (form data)
    
    # Extract user information from the request
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    phone_number = data.get('phoneNumber')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check if required fields are provided
    if not all([first_name, last_name, email, phone_number, username, password]):
        return jsonify({"error": "All fields are required!"}), 400

    # Validate if the username or phone number is already taken (if necessary)
    existing_user = User.query.filter((User.username == username) | (User.phone_number == phone_number) | (User.email == email)).first()
    if existing_user:
        return jsonify({"error": "Username or phone number already exists!"}), 400

    # Hash the password before storing it
    hashed_password = generate_password_hash(password)

    # Create a new user record
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        username=username,
        password=hashed_password
    )

    # Save the user to the database
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully!"}), 201
    except IntegrityError:
        db.session.rollback()  # Rollback in case of error
        return jsonify({"error": "Database integrity error, possibly due to duplicate entry!"}), 400
    except Exception as e:
        db.session.rollback()  # Rollback in case of other errors
        return jsonify({"error": "Error registering user", "details": str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required!"}), 400

    # Find the user by username
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials!"}), 401

    # Create JWT token with the user ID and role
    token = jwt.encode({
        'user_id': user.id,
        'role': user.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm="HS256")

    # Set the token in a cookie for authentication in future requests
    response = make_response(jsonify({"message": "Login successful!"}))
    response.set_cookie(
        'token', token, secure=True, samesite="None", path="/"
    )  # HTTPOnly cookie for security
    return response


@auth_bp.route('/logout', methods=['GET'])
def logout():
   response = make_response(jsonify({"message": "Logout successful"}))
   response.set_cookie('token', '', expires=0, httponly=True)  # Clear JWT cookie
   return response


@token_required
@role_required('admin')
def admin_only_resource():
    return jsonify({"message": f"Welcome, {request.current_user.username}!"}), 200


@auth_bp.route('/dashboard', methods=['GET'])
@token_required
@role_required('admin', 'manager')
def dashboard():
    return jsonify({"message": "Welcome to the dashboard!"}), 200


@auth_bp.route('/home', methods=['GET'])
@token_required
@role_required('user')
def home():
    return jsonify("Welcome to the home page!"), 200


@auth_bp.route('/contact', methods=['GET'])
@token_required
@role_required('user')
def Contact():
    return jsonify("Welcome to the contact page!"), 200


@auth_bp.route('/forgotpassword', methods=['POST'])
def forgot_password():
    email = request.get_json().get('email')
    if not email:
        return jsonify({"error": "Email is required!"}), 400

    user = User.query.filter_by(email=email).first()

    if user:
        # Generate a password reset token
        token = s.dumps(user.email, salt=os.getenv("PASSWORD_RESET_SALT"))
        reset_url = f"http://localhost:5173/resetpassword/{token}"

        # Send email with the reset URL (you need to configure your SMTP settings)
        msg = Message("Password Reset Request", sender=os.getenv("MAIL_USERNAME"), recipients=[email])
        msg.body = f"Click the following link to reset your password: {reset_url}"
        mail.send(msg)

        return jsonify({"message": "Password reset link has been sent to your email."}), 200
    else:
        return jsonify({"error": "Email not found!"}), 404


@auth_bp.route('/resetpassword/<token>', methods=['POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt=os.getenv("PASSWORD_RESET_SALT"), max_age=3600)  # Token expires after 1 hour
    except Exception as e:
        return jsonify({"error": "The reset link is invalid or has expired."}), 400

    data = request.get_json()
    new_password = data.get('newPassword')
    if not new_password:
        return jsonify({"error": "New password is required!"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found!"}), 404

    # Hash the new password and update in the database
    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": "Your password has been reset successfully!"}), 200