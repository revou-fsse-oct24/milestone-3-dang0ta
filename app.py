from flask import Flask, request
from werkzeug import exceptions

from db import UserRepository, AccountRepository, TransactionRepository
from app_config import AppConfig
from routes import auth_bp, user_bp, accounts_bp, transaction_bp
from auth import AuthRepository

def create_app(users: UserRepository, auth: AuthRepository, accounts: AccountRepository, transactions: TransactionRepository):
    app = Flask(__name__)
    app.config.from_object(AppConfig())
    app.register_blueprint(auth_bp(auth))
    app.register_blueprint(user_bp(users, auth))
    app.register_blueprint(accounts_bp(accounts))
    app.register_blueprint(transaction_bp(transactions))

    @app.errorhandler(exceptions.NotFound)
    def handle_notfound(e):
        return "not found", 404
    
    @app.errorhandler(exceptions.InternalServerError)
    def handle_internal_error(e):
        return "internal server error", 500
        
    return app