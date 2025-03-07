from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from db import AccountRepository
from auth_jwt import jwt_required, get_jwt_identity
from models import Account

def accounts_bp(accounts: AccountRepository):
    bp = Blueprint("account", __name__, url_prefix="/accounts")

    @bp.route("/", methods=["GET", "POST"])
    @jwt_required
    def handle_root():
        match request.method:
            case "GET":
                return get_accounts(accounts)
            case "POST":
                return create_account(accounts)
            case _:
                return "Method not allowed", 405
    
    @bp.route("/<string:id>", methods=["GET", "PUT", "DELETE"])
    @jwt_required
    def handle_id(id:str):
        match request.method:
            case "GET":
                return get_account(accounts, id)
            case "PUT":
                return update_account(accounts, id)
            case "DELETE":
                return delete_account(accounts, id)
            case _:
                return "Method not allowed", 405
    
    return bp

def get_accounts(accounts: AccountRepository):
    current_user = get_jwt_identity()
    if current_user == None:
        return "Unauthorized", 403
    
    acc = accounts.find_by_user_id(current_user)
    return jsonify({"accounts": list(acc)}), 200

def create_account(accounts: AccountRepository):
    try:
        acc = Account(**request.get_json())
        acc_dict = accounts.create(data=acc.model_dump())
        return jsonify({"account": acc_dict}), 200
    except ValidationError as e:
        return e.errors(), 400

def get_account(accounts: AccountRepository, id: str):
    acc = accounts.find_by_id(id)
    if acc == None:
        return "account can't be found", 404
    
    return jsonify({"account": acc}), 200

def update_account(accounts: AccountRepository, id: str):
    try:
        acc = accounts.find_by_id(id)
        if acc == None:
            return "account can't be found", 404
        
        updated_acc = Account(**request.get_json())
        acc.update(updated_acc.model_dump())
        return jsonify({"account": acc}), 200
    except ValidationError as e:
        return e.errors(), 400
    except KeyError as e:
        return str(e), 400
    except ValueError as e:
        return str(e), 400
    
def delete_account(accounts: AccountRepository, id:str):
    acc = accounts.find_by_id(id)
    if acc == None:
        return jsonify({"result": "not_found"}), 200
    
    accounts.delete(id)
    return jsonify({"result": "deleted"}), 200