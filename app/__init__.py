from flask import Flask
from app.utils import db
from app.routes import init_routes
from app.config import Config
from flask_cors import CORS
from app.utils import mail
from app.utils import mongo

def create_app():
    app = Flask(__name__)

    # Initialize CORS (Cross-Origin Resource Sharing)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # Configure the app using your custom config
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Initialize Flask-Mail
    mail.init_app(app)

    # Initialize mongo
    mongo.init_app(app)

    # Register your blueprints (routes)
    init_routes(app)

    # Create database tables (e.g., User, etc.)
    with app.app_context():
        db.create_all()

    return app

