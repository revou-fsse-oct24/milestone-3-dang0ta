from flask import Flask, request
from werkzeug import exceptions

from db import UserRepository, AccountRepository, TransactionRepository
from app_config import AppConfig
from routes import auth_bp, user_bp, accounts_bp, transaction_bp
from auth import AuthRepository

class DependencyContainer:
    def __init__(self, app=None, *, users: UserRepository=None, auth: AuthRepository=None, accounts: AccountRepository=None, transactions: TransactionRepository=None):
        self.app = app
        self.users =  users or UserRepository({})
        self.auth = auth or AuthRepository()
        self.accounts = accounts or AccountRepository({})
        self.transactions = transactions or TransactionRepository({})

def create_app(dependencies=None, test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(AppConfig())
    
    # Override config with test_config if provided
    if test_config:
        app.config.update(test_config)
    
    # Initialize or use provided dependencies
    if dependencies is None:
        dependencies = DependencyContainer(app=app)
    
    # Store dependencies in app context for access in other places if needed
    app.dependencies = dependencies
    
    # Register blueprints
    app.register_blueprint(auth_bp(dependencies.auth))
    app.register_blueprint(user_bp(dependencies.users, dependencies.auth))
    app.register_blueprint(accounts_bp(dependencies.accounts))
    app.register_blueprint(transaction_bp(dependencies.transactions))

    @app.errorhandler(exceptions.NotFound)
    def handle_notfound(e):
        return "not found", 404
    
    @app.errorhandler(exceptions.InternalServerError)
    def handle_internal_error(e):
        return "internal server error", 500
        
    return app