from .auth_routes import auth_bp
from .users import users_bp

def init_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)

