from flask import Blueprint, jsonify
from app.models import User

users_bp = Blueprint('users', __name__)

# get all users
@users_bp.route('/users', methods=['GET'])
def all_users():
    users = User.query.all()
    return jsonify({"total": len(users)})


