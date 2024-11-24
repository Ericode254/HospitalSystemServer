import pytest
from app import create_app, db

@pytest.fixture
def test_client():
    app = create_app()  # Load test configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory DB

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Set up tables
        yield client  # Provide the test client
        with app.app_context():
            db.session.remove()
            db.drop_all()  # Clean up

def test_register_user(test_client):
    data = {
        "firstName": "John",
        "lastName": "Doe",
        "phoneNumber": "1234567890",
        "username": "johndoe",
        "email": "johndoe@example.com",
        "password": "SecureP@ssw0rd"
    }
    response = test_client.post('/register', json=data)
    assert response.status_code == 201
    assert b"User registered successfully!" in response.data

def test_login_user(test_client):
    # Register a user first
    test_client.post('/register', json={
        "firstName": "Jane",
        "lastName": "Smith",
        "phoneNumber": "9876543210",
        "username": "janesmith",
        "email": "janesmith@example.com",
        "password": "AnotherP@ssw0rd"
    })

    # Login with the registered user
    response = test_client.post('/login', json={
        "username": "janesmith",
        "password": "AnotherP@ssw0rd"
    })
    assert response.status_code == 200
    assert b"Login successful!" in response.data


def test_forgot_password(mocker, test_client):
    # Mock the mail.send method
    mock_mail = mocker.patch('app.utils.mail.send')  # Replace 'app.utils.mail.send' with the correct import path
    mock_mail.return_value = True  # Set a return value for the mocked method

    # Test data
    email = "test@example.com"

    # Prepopulate the database with a test user
    from app.models import User
    test_user = User(
        first_name="Test",
        last_name="User",
        email=email,
        phone_number="1234567890",
        username="testuser",
        password="hashedpassword"  # Ensure this matches your password hashing logic
    )
    with test_client.application.app_context():
        from app.utils import db
        db.session.add(test_user)
        db.session.commit()

    # Make the request
    response = test_client.post('/forgotpassword', json={"email": email})

    # Assertions
    assert response.status_code == 200
    assert b"Password reset link has been sent to your email." in response.data

    # Check if mail.send was called with the correct arguments
    assert mock_mail.called
    assert mock_mail.call_count == 1
    assert mock_mail.called
