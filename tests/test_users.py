from flask import json
import pytest
from app.models import User
from app import create_app, db

@pytest.fixture
def test_client():
    """Fixture to set up the Flask test client."""
    app = create_app()  # Your function to initialize the Flask app
    app.config['TESTING'] = True  # Enable testing mode
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Set up the database schema
            yield client  # Provide the test client to tests
            db.session.remove()
            db.drop_all()

@pytest.fixture
def mock_users():
    """Fixture to provide mock user data."""
    return [
        User(first_name="John", last_name="Doe", username="johndoe", email="john@example.com", phone_number="1234567890"),
        User(first_name="Jane", last_name="Doe", username="janedoe", email="jane@example.com", phone_number="0987654321")
    ]


def test_all_users(test_client):
    """Test the GET /users route."""
    response = test_client.get('/users')
    assert response.status_code == 200

# def test_update_user_success(test_client):
#     """Test the PUT /users/<user_id> route for successful update."""
#     user_id = User.query.all()[0].id
#     response = test_client.put(f'/users/{user_id}', json={'role': 'admin'})
#     assert response.status_code == 200
#     assert response.json['message'] == "User updated successfully"
#

def test_update_user_not_found(test_client, mocker):
    """Test the PUT /users/<user_id> route for user not found."""
    mocker.patch('app.models.User.query.get', return_value=None)

    response = test_client.put('/users/999', json={'role': 'admin'})
    assert response.status_code == 404
    assert response.json['error'] == "User not found"


# def test_delete_user_success(test_client, mocker, mock_users):
#     """Test the DELETE /users/<user_id> route for successful deletion."""
#     user_to_delete = mock_users[0]
#     mocker.patch('app.models.User.query.get', return_value=user_to_delete)
#     mock_delete = mocker.patch('app.utils.db.session.delete')
#     mock_commit = mocker.patch('app.utils.db.session.commit')
#
#     response = test_client.delete('/users/1')
#     assert response.status_code == 200
#     assert response.json['message'] == "User deleted successfully"
#
#     # Ensure the user was deleted and committed
#     mock_delete.assert_called_once_with(user_to_delete)
#     mock_commit.assert_called_once()
#

def test_delete_user_not_found(test_client, mocker):
    """Test the DELETE /users/<user_id> route for user not found."""
    mocker.patch('app.models.User.query.get', return_value=None)

    response = test_client.delete('/users/999')
    assert response.status_code == 404
    assert response.json['error'] == "User not found"
