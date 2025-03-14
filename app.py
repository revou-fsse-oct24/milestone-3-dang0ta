from flask import Flask, request
from werkzeug import exceptions

from db_inmemory import UserRepository, AccountRepository, TransactionRepository
from db import *
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
    app.config.from_object(AppConfig())

    if test_config:
        app.config.update(test_config)

    if dependencies is None:
        dependencies = DependencyContainer(app=app)
    app.dependencies = dependencies
    
    # Register blueprints
    app.register_blueprint(auth_bp())
    app.register_blueprint(user_bp())
    app.register_blueprint(accounts_bp(dependencies.accounts))
    app.register_blueprint(transaction_bp(dependencies.transactions))

    @app.errorhandler(exceptions.NotFound)
    def handle_notfound(e):
        return "not found", 404
    
    @app.errorhandler(exceptions.InternalServerError)
    def handle_internal_error(e):
        return "internal server error", 500
        
    return app