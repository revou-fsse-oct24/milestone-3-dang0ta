from flask import Flask, jsonify
from flask_migrate import Migrate
from werkzeug import exceptions
from routes import register_bp
from db import init_db, db_session, DB

def create_app():
    """Create and configure the Flask application"""
    try:
        app = Flask(__name__)
        init_db()
        register_bp(app)
        migrate = Migrate(app=app, db=DB)

        @app.route("/")
        def ping():
            return jsonify({"status": "OK"}), 200

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            db_session.remove()

        @app.errorhandler(exceptions.NotFound)
        def handle_notfound(e):
            db_session.rollback()
            return jsonify({"error": "not found"}), 404
        
        @app.errorhandler(exceptions.InternalServerError)
        def handle_internal_error(e):
            db_session.rollback()
            return jsonify({"error": "internal server error"}), 500

        @app.errorhandler(exceptions.Forbidden)
        def handle_forbidden(e):
            db_session.rollback()
            return jsonify({"error": "Forbidden"}), 401
            
        return app
    except Exception as e:
        print(f"Error creating app: {e}")
        raise e

    