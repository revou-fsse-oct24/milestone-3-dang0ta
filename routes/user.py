from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from models import UserCredential, UserInformation, CreateUserRequest
from auth_jwt import jwt_required, get_jwt_identity
from db.users import create_user as db_create_user
from db.users import get_user as db_get_user
from db.users import update_user as db_update_user
from db.users import UserNotFoundException

def user_bp()-> Blueprint:
    bp = Blueprint("users", __name__, url_prefix="/users")

    @bp.route("/", methods=["POST"])
    def create_user():
        try:
            req = CreateUserRequest(**request.get_json())
            id = db_create_user(req)
            
            return jsonify({"id": id}), 201
        except ValidationError as e:
            errors = e.errors()
            for error in errors:
                if error['loc'][0] == 'name' and error['msg'] == 'Field required':
                    return jsonify({"error": "missing user name"}), 400
                if error['loc'][0] == 'email_address' and error['msg'] == 'Field required':
                    return jsonify({"error": "missing email address"}), 400
                if error['loc'][0] == 'email_address':
                    return jsonify({"error": "invalid email address"}), 400
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
    try:
        current_user = get_jwt_identity()
        user = db_get_user(current_user)
        return jsonify(user.model_dump()), 200
    except UserNotFoundException as e:
        return jsonify({"error": "user not found"}), 404


def handle_update_me():
    try:
        current_user = get_jwt_identity()
        updated = db_update_user(current_user, UserInformation(**request.get_json()))
        return jsonify(updated.model_dump()), 200
    except ValidationError as e:
        errors = e.errors()
        for error in errors:
            if error['loc'][0] == 'name' and error['msg'] == 'Field required':
                return jsonify({"error": "missing user name"}), 400
            if error['loc'][0] == 'email_address' and error['msg'] == 'Field required':
                return jsonify({"error": "missing email address"}), 400
            if error['loc'][0] == 'email_address':
                return jsonify({"error": "invalid email address"}), 400
        return e.errors(), 400
    except ValueError as e:
        return str(e), 400
    except UserNotFoundException as e:
        return jsonify({"error": str(e)}), 404
