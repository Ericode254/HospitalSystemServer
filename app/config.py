import os

class Config:
    # General configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")  # Always use a secret key for encryption

    # Mail configuration (Using environment variables for better security)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "your-email@gmail.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "your-email-password")
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))  # Convert to integer from string
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() in ["true", "1", "t"]  # Convert to boolean

    # Password reset token settings
    PASSWORD_RESET_SALT = os.getenv("PASSWORD_RESET_SALT", "password-reset-salt")

    # mongo uri
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///default.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable Flask-SQLAlchemy modification tracking

