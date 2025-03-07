from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from typing import Dict

from db import UserRepository
from models import UserCredential, UserInformation
from auth_jwt import jwt_required, get_jwt_identity
from auth import AuthRepository

def user_bp(users: UserRepository, auth: AuthRepository)-> Blueprint:
    bp = Blueprint("users", __name__, url_prefix="/users")

    @bp.route("/", methods=["POST"])
    def create_user():
        try:
            user = UserCredential(**request.get_json())
            dict = users.create(data = user.model_dump())
            
            auth.register(email=user.email, password=user.password, user_id=dict["id"])
            
            return dict["id"], 201
        except ValidationError as e:
            return e.errors(), 400
        
    @bp.route("/me", methods=["GET", "PUT"])
    @jwt_required
    def handle_me():
        match request.method:
            case "GET":
                return handle_get_me(users)
            case "PUT":
                return handle_update_me(users)
            case _:
                return "Method not allowed", 405
            
    return bp

def handle_get_me(users: UserRepository):
    current_user = get_jwt_identity()
    user_dict = users.find_by_id(current_user)
    if user_dict == None:
        return "user not found", 404

    return jsonify(user_dict), 200

def handle_update_me(users: UserRepository):
    try:
        current_user = get_jwt_identity()
        current_me = users.find_by_id(current_user)
        if current_me == None:
            return "user not found", 404
        
        updated_me = UserInformation(**request.get_json()).model_dump()
        current_me.update(updated_me)
        print(f"updated_me: {updated_me}, current_me: {current_me}")
        updated_dict = users.update(id=current_user, data=current_me)
        return jsonify(updated_dict), 200
    except ValidationError as e:
        return e.errors(), 400
