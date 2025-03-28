from flask import Flask
from werkzeug import exceptions
from app_config import AppConfig
from routes import register_bp
from db import db_session, init_db

def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(AppConfig())
    init_db()

    if test_config:
        app.config.update(test_config)
    
    register_bp(app)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    @app.errorhandler(exceptions.NotFound)
    def handle_notfound(e):
        return "not found", 404
    
    @app.errorhandler(exceptions.InternalServerError)
    def handle_internal_error(e):
        return "internal server error", 500
        
    return app