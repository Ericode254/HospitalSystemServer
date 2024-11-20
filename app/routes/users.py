from flask import Blueprint, jsonify, request
from app.models import User
from app.utils import db

users_bp = Blueprint('users', __name__)

# Helper function to serialize user
def user_to_dict(user):
    return {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'email': user.email,
        'phone_number': user.phone_number,
        'role': user.role
    }

# Get all users
@users_bp.route('/users', methods=['GET'])
def all_users():
    users = User.query.all()
    return jsonify([user_to_dict(user) for user in users])

# Flask route to update user role
@users_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = User.query.get(user_id)  # Find the user by ID
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update the user role
        new_role = request.json.get('role')  # Role sent from the client (e.g., "admin" or "user")
        user.role = new_role

        db.session.commit()  # Commit the change to the database
        return jsonify({"message": "User updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Flask route to delete a user
@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get(user_id)  # Find the user by ID
        if not user:
            return jsonify({"error": "User not found"}), 404

        db.session.delete(user)  # Delete the user from the database
        db.session.commit()  # Commit the change to the database
        return jsonify({"message": "User deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
