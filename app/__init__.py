from flask import Flask
from app.utils import db
from app.routes import init_routes
from app.config import Config
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}},supports_credentials=True)
    # Configure app
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    init_routes(app)
    # Create database tables
    with app.app_context():
        db.create_all()

    return app

