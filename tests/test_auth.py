import pytest
from flask import Flask
from app import create_app, db
from app.models import User
from flask_testing import TestCase
import json

class AuthTestCase(TestCase):
    def create_app(self):
        # Create a test instance of your app
        app = create_app()  # Assuming you have different configs for testing
        return app

    def setUp(self):
        # Set up the database before each test
        db.create_all()

        # Add a test user to the database
        self.test_user = User(
            first_name="John",
            last_name="Doe",
            phone_number="1234567890",
            username="johndoe",
            email="john@example.com",
            password="password"
        )
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        # Clean up after each test
        db.session.remove()
        db.drop_all()

    # Test user registration
    def test_register_user(self):
        response = self.client.post('/register', json={
            "firstName": "Jane",
            "lastName": "Doe",
            "phoneNumber": "0987654321",
            "username": "janedoe",
            "email": "jane@example.com",
            "password": "password"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('User registered successfully!', response.json['message'])

    # Test user login
    def test_login_user(self):
        response = self.client.post('/login', json={
            "username": "johndoe",
            "password": "password"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Login successful!', response.json['message'])

    # Test user login with incorrect credentials
    def test_login_user_invalid(self):
        response = self.client.post('/login', json={
            "username": "johndoe",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid credentials!', response.json['error'])

    # Test user logout
    def test_logout_user(self):
        # First, log in the user
        self.client.post('/login', json={
            "username": "johndoe",
            "password": "password"
        })
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Logout successful', response.json['message'])

    # Test access to protected route (admin)
    def test_access_admin_only_resource(self):
        # First, login and get the token
        response = self.client.post('/login', json={
            "username": "johndoe",
            "password": "password"
        })
        token = response.cookies.get('token')

        # Now access the admin-only resource with token
        response = self.client.get('/dashboard', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Welcome to the dashboard!', response.json['message'])

    # Test forgot password
    def test_forgot_password(self):
        response = self.client.post('/forgotpassword', json={
            'email': 'john@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Password reset link has been sent to your email.', response.json['message'])

    # Test password reset with valid token
    def test_reset_password(self):
        # Assume you have a valid token generated
        token = 'valid_token_for_testing'

        response = self.client.post(f'/resetpassword/{token}', json={
            'newPassword': 'newpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Your password has been reset successfully!', response.json['message'])

    # Test stroke prediction (mock the model)
    def test_predict_stroke(self):
        response = self.client.post('/predict', json={
            'gender': 'Male',
            'age': 45,
            'hypertension': 1,
            'ever_married': 'Yes',
            'work_type': 'Private',
            'Residence_type': 'Urban',
            'avg_glucose_level': 100,
            'bmi': 28.5,
            'smoking_status': 'never smoked'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('stroke_risk', response.json)
        self.assertIn('prediction', response.json)

if __name__ == '__main__':
    pytest.main()
