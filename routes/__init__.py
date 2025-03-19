from .auth import auth_bp
from .user import user_bp
from .accounts import accounts_bp
from .transactions import transaction_bp
from flask import Flask

def register_bp(app: Flask):
    app.register_blueprint(auth_bp())
    app.register_blueprint(user_bp())
    app.register_blueprint(accounts_bp())
    app.register_blueprint(transaction_bp())