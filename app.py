from flask import Flask, request
from werkzeug import exceptions

from db_inmemory import TransactionRepository
from app_config import AppConfig
from routes import auth_bp, user_bp, accounts_bp, transaction_bp
from db import Session
from sqlalchemy.orm import scoped_session

def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(AppConfig())
    app.Session = scoped_session(session_factory=Session)

    if test_config:
        app.config.update(test_config)
    
    # Register blueprints
    app.register_blueprint(auth_bp())
    app.register_blueprint(user_bp())
    app.register_blueprint(accounts_bp())
    app.register_blueprint(transaction_bp(TransactionRepository({})))

    @app.errorhandler(exceptions.NotFound)
    def handle_notfound(e):
        return "not found", 404
    
    @app.errorhandler(exceptions.InternalServerError)
    def handle_internal_error(e):
        return "internal server error", 500
        
    return app