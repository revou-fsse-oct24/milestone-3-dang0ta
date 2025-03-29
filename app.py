from flask import Flask
from werkzeug import exceptions
from routes import register_bp
from db import init_db, db_session, db_session

def create_app():
    """Create and configure the Flask application"""
    try:
        app = Flask(__name__)
        init_db()
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
    except Exception as e:
        print(f"Error creating app: {e}")
        raise e

    