from flask import Flask, request
from pydantic import ValidationError
from flask_jwt_extended  import JWTManager, jwt_required, get_jwt_identity, create_access_token

from src.db import UserRepository
from src.models import User
from src.app_config import AppConfig
from src.auth import AuthRepository, WrongCredentialException, UserNotFoundException

def create_app(users: UserRepository, auth: AuthRepository):
    app = Flask(__name__)
    app.config.from_object(AppConfig)
    jwt = JWTManager()

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
    
    @app.route("/login", methods=["POST"])
    def login():
        try:
            data = request.json
            email = data.get("email")
            password = data.get("password")
            user_id = auth.authenticate(email, password)
            access_token = create_access_token(identity=user_id)
            return access_token, 200
        except ValidationError as e:
            return e.errors(), 400
        except WrongCredentialException as e:
            # TODO: log the email
            return str(e), 403
        except UserNotFoundException as e:
            # TODO: log the email
            return str(e), 403
        except Exception as e:
            return str(e), 500
        
    @app.route("/users/me", methods=["GET"])
    @jwt_required()
    def get_current_user():
        try:
            current_user = get_jwt_identity()
            user_dict = users.find_by_id(current_user)
            if user_dict == None:
                return "user not found", 404

            return user_dict, 200
        except Exception as e:
            return str(e), 500
        
    return app