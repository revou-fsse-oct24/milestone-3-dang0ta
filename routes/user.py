from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from db import UserRepository
from models import User
from auth_jwt import jwt_required, get_jwt_identity
from auth import AuthRepository

def user_bp(users: UserRepository, auth: AuthRepository)-> Blueprint:
    bp = Blueprint("users", __name__, url_prefix="/users")

    @bp.route("/", methods=["POST"])
    def create_user():
        try:
            user = User(**request.get_json())
            dict = users.create(data = user.model_dump())
            
            auth.register(email=user.email, password=user.password, user_id=dict["id"])
            
            return dict["id"], 201
        except ValidationError as e:
            return e.errors(), 400
        except Exception as e:
            return str(e), 500
        
    @bp.route("/me", methods=["GET"])
    @jwt_required
    def get_current_user():
        try:
            current_user = get_jwt_identity()
            print(current_user)
            user_dict = users.find_by_id(current_user)
            if user_dict == None:
                return "user not found", 404

            user_dict.pop("password")
            return jsonify(user_dict), 200
        except Exception as e:
            return str(e), 500
        
    return bp