from flask import Blueprint, jsonify, request, Response
from pydantic import ValidationError
from auth_jwt import jwt_required, get_jwt_identity
from models import Account, CreateAccountRequest, UpdateAccountRequest

from shared.exceptions import parseValidationError
from db.accounts import get_account as db_get_account
from db.accounts import get_accounts as db_get_accounts
from db.accounts import update_account as db_update_account
from db.accounts import create_account as db_create_account
from db.accounts import delete_account as db_delete_account
from db.accounts import AccountsNotFoundException, AccountNotFoundException
from rbac.route import is_account_belong_to_current_user, role_required

def accounts_bp():
    bp = Blueprint("account", __name__, url_prefix="/accounts")

    @bp.route("/", methods=["GET", "POST", "PUT"])
    @jwt_required
    def handle_root():
        match request.method:
            case "GET":
                return get_accounts()
            case "POST":
                return create_account()
            case "PUT": 
                return update_default_account()
    
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
    
    return bp

def get_accounts():
    try:
        current_user = get_jwt_identity()
        acc = db_get_accounts(user_id=current_user)
        return jsonify({"accounts": [acc.model_dump() for acc in acc]}), 200
    except AccountsNotFoundException:
        return jsonify({"error": "no account found for the user"}), 404

def create_account():
    try:
        current_user = get_jwt_identity()
        account = db_create_account(
            user_id=current_user, 
            request=CreateAccountRequest(**request.get_json())
        )
        dump = account.model_dump()
        return jsonify({"account":dump }), 201
    except ValidationError as e:
        # TODO: logging: log the error detail here, use structured logging.
        if e.title == "CreateAccountRequest":            
            return parseValidationError(e, 400)
        
        return jsonify({"error": "server responded with invalid data"}), 500

def get_account(id: str):
    try:
        if not is_account_belong_to_current_user(id):
            return jsonify({"error": "Forbidden"}), 401
        
        current_user = get_jwt_identity()
        acc = db_get_account(user_id=current_user, account_id=id)
        return jsonify(acc.model_dump()), 200
    except AccountNotFoundException:
        return jsonify({"error": "Account not found"}), 404


# @role_required("admin") # updating a specific account can only be done by admins
def update_account(id: str):
    try:
        current_user = get_jwt_identity()
        req = UpdateAccountRequest(**request.get_json())
        req.account_id = id
        account = db_update_account(user_id=current_user,request=req)
        return jsonify(account.model_dump()), 200
    except ValidationError as e:
        if e.title == "UpdateAccountRequest":                
            errors = e.errors()
            if not errors:
                return jsonify({"error": "Invalid account data"}), 400
                
            error = errors[0]
            field = error.get("loc", [])[0] if error.get("loc") else "unknown"
            return jsonify({"error": f"invalid {field}"}), 400
        return jsonify({"error": "the server responded with invalid data"}), 500

    except AccountNotFoundException:
        return jsonify({"error": "Account not found"}), 404
    except AccountsNotFoundException:
        return jsonify({"error": "Account not found"}), 404
    
def update_default_account():
    try:
        current_user = get_jwt_identity()
        req = UpdateAccountRequest(**request.get_json())
        account = db_update_account(user_id=current_user,request=req)
        return jsonify(account.model_dump()), 200
    except ValidationError as e:
        errors = e.errors()
        if not errors:
            return jsonify({"error": "Invalid account data"}), 400
            
        error = errors[0]
        field = error.get("loc", [])[0] if error.get("loc") else "unknown"
        return jsonify({"error": f"invalid {field}"}), 400
    except AccountsNotFoundException:
        return jsonify({"error": "Account not found"}), 404
    
def delete_account(id:str):
    try:
        if not is_account_belong_to_current_user(id):
            return jsonify({"error": "Forbidden"}), 401
        
        current_user = get_jwt_identity()
        db_delete_account(user_id=current_user, account_id=id)
        return jsonify({"result": "deleted"}), 200
    except AccountNotFoundException:
        return jsonify({"error": "Account not found"}), 404
    
