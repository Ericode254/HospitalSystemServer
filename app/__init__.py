from flask import Flask
from app.utils import db
from app.routes import auth
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app

