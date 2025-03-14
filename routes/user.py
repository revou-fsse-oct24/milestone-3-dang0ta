from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from models import UserCredential, UserInformation
from auth_jwt import jwt_required, get_jwt_identity
from db.users import create_user as db_create_user
from db.users import get_user as db_get_user
from db.users import update_user as db_update_user

def user_bp()-> Blueprint:
    bp = Blueprint("users", __name__, url_prefix="/users")

    @bp.route("/", methods=["POST"])
    def create_user():
        try:
            user = UserCredential(**request.get_json())
            id = db_create_user(user=user)
            
            return jsonify({"id": id}), 201
        except ValidationError as e:
            errors = e.errors()
            for error in errors:
                if error['loc'][0] == 'name' and error['msg'] == 'Field required':
                    return jsonify({"error": "missing user name"}), 400
                if error['loc'][0] == 'email' and error['msg'] == 'Field required':
                    return jsonify({"error": "missing email"}), 400
                if error['loc'][0] == 'email':
                    return jsonify({"error": "invalid email"}), 400
                if error['loc'][0] == 'password' and error['msg'] == 'Field required':
                    return jsonify({"error": "missing password"}), 400

            return e.errors(), 400
        
    @bp.route("/me", methods=["GET", "PUT"])
    @jwt_required
    def handle_me():
        match request.method:
            case "GET":
                return handle_get_me()
            case "PUT":
                return handle_update_me()
            case _:
                return "Method not allowed", 405
            
    return bp

def handle_get_me():
    current_user = get_jwt_identity()
    user = db_get_user(current_user)
    if user is None:
        return "user not found", 404

    return jsonify({"user": user}), 200

def handle_update_me():
    try:
        current_user = get_jwt_identity()
        updated = db_update_user(current_user, UserInformation(**request.get_json()).model_dump())
        return jsonify({"user": updated}), 200
    except ValidationError as e:
        return e.errors(), 400
    except ValueError as e:
        return str(e), 400
