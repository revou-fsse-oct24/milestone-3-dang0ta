from flask import Flask, request
from werkzeug import exceptions

from db import UserRepository
from app_config import AppConfig
from routes import auth_bp, user_bp
from auth import AuthRepository

def create_app(users: UserRepository, auth: AuthRepository):
    app = Flask(__name__)
    app.config.from_object(AppConfig())
    app.register_blueprint(auth_bp(auth))
    app.register_blueprint(user_bp(users, auth))

    @app.errorhandler(exceptions.NotFound)
    def handle_notfound(e):
        return "not found", 404
    
    @app.errorhandler(exceptions.InternalServerError)
    def handle_internal_error(e):
        return "internal server error", 500
        
    return app