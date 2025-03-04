from flask import Flask, request
from pydantic import ValidationError
from src.db import UserRepository
from src.models import User

def create_app(users: UserRepository):
    app = Flask(__name__)

    @app.route("/users", methods=['POST'])
    def create_user():
        try:
            user = users.create(
                data = User(**request.get_json()).model_dump())

            return user, 201
        except ValidationError as e:
            return e.errors(), 400
        except Exception as e:
            return str(e), 500
        
    return app