from flask import Blueprint, request, jsonify, make_response
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import datetime
from app.models import User
from functools import wraps
import os
from app.utils import db
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__)

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
    password = data.get('password')

    # Check if required fields are provided
    if not all([first_name, last_name, phone_number, username, password]):
        return jsonify({"error": "All fields are required!"}), 400

    # Validate if the username or phone number is already taken (if necessary)
    existing_user = User.query.filter((User.username == username) | (User.phone_number == phone_number)).first()
    if existing_user:
        return jsonify({"error": "Username or phone number already exists!"}), 400

    # Hash the password before storing it
    hashed_password = generate_password_hash(password)

    # Create a new user record
    new_user = User(
        first_name=first_name,
        last_name=last_name,
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

