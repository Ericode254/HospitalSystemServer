from flask import Blueprint, request, jsonify
from app.services import create_user

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    try:
        user = create_user(data)
        return jsonify({"message": "User created successfully", "user": user}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
