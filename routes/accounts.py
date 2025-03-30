from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from auth_jwt import jwt_required, get_jwt_identity
from models import Account

from db.accounts import get_account as db_get_account
from db.accounts import get_accounts as db_get_accounts
from db.accounts import update_account as db_update_account
from db.accounts import create_account as db_create_account
from db.accounts import delete_account as db_delete_account
from db.accounts import AccountsNotFoundException, AccountNotFoundException

def accounts_bp():
    bp = Blueprint("account", __name__, url_prefix="/accounts")

    @bp.route("/", methods=["GET", "POST"])
    @jwt_required
    def handle_root():
        match request.method:
            case "GET":
                return get_accounts()
            case "POST":
                return create_account()
            case _:
                return jsonify({"error": "Method not allowed"}), 405
    
    @bp.route("/<string:id>", methods=["GET", "PUT", "DELETE"])
    @jwt_required
    def handle_id(id:str):
        match request.method:
            case "GET":
                return get_account(id)
            case "PUT":
                return update_account(id)
            case "DELETE":
                return delete_account(id)
            case _:
                return jsonify({"error": "Method not allowed"}), 405
    
    return bp

def get_accounts():
    try:
        current_user = get_jwt_identity()
        if current_user is None:
            return jsonify({"error": "Unauthorized"}), 401
        
        acc = db_get_accounts(user_id=current_user)
        return jsonify({"accounts": [acc.model_dump() for acc in acc]}), 200
    except AccountsNotFoundException:
        return jsonify({"accounts": []}), 200

def create_account():
    try:
        current_user = get_jwt_identity()
        if current_user is None:
            return jsonify({"error": "Unauthorized"}), 403
        
        acc = Account(**request.get_json())

        id=db_create_account(user_id=current_user, account=acc)
        return jsonify({"account_id": id}), 201
    except ValidationError as e:
        errors = e.errors()
        if not errors:
            return jsonify({"error": "Invalid account data"}), 400
            
        error = errors[0]
        field = error.get("loc", [])[0] if error.get("loc") else "unknown"
        return jsonify({"error": f"invalid {field}"}), 400

def get_account(id: str):
    try:
        current_user = get_jwt_identity()
        acc = db_get_account(user_id=current_user, account_id=id)
        return jsonify(acc.model_dump()), 200
    except AccountNotFoundException:
        return jsonify({"error": "Account not found"}), 404

def update_account(id: str):
    try:
        current_user = get_jwt_identity()
        account = Account(**request.get_json())
        db_update_account(user_id=current_user, account_id=id, account=account)
        return jsonify(account.model_dump()), 200
    except ValidationError as e:
        errors = e.errors()
        if not errors:
            return jsonify({"error": "Invalid account data"}), 400
            
        error = errors[0]
        field = error.get("loc", [])[0] if error.get("loc") else "unknown"
        return jsonify({"error": f"invalid {field}"}), 400

    except AccountNotFoundException:
        return jsonify({"error": "Account not found"}), 404
    
    except KeyError as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
def delete_account(id:str):
    try:
        current_user = get_jwt_identity()
        db_delete_account(user_id=current_user, account_id=id)
        return jsonify({"result": "deleted"}), 200
    except AccountNotFoundException:
        return jsonify({"error": "Account not found"}), 404