from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from auth_jwt import jwt_required, get_jwt_identity
from db.transactions import withdraw
from db.transactions import deposit
from db.transactions import transfer
from db.transactions import get_transactions as db_get_transactions
from db.transactions import get_transaction as db_get_transaction
from db.transactions import TransactionNotFoundException
from db.transactions import TransactionQuery
from db.transactions import get_categories
from db.accounts import AccountsNotFoundException, AccountNotFoundException
from models import WithdrawRequest, DepositRequest, TransferRequest
from typing import List
from shared.exceptions import parseValidationError
from rbac.route import is_account_belong_to_current_user

def transaction_bp() -> Blueprint:
    bp = Blueprint("transactions", __name__, url_prefix="/transactions")

    @bp.route("/categories")
    @jwt_required
    def handle_categories():
        current_user = get_jwt_identity()
        categories = get_categories(user_id=current_user)
        return jsonify({"categories": categories})

    @bp.route("/withdraw", methods=["POST"])
    @jwt_required
    def handle_withdraw():
        try:
            withdraw_request = WithdrawRequest(**request.get_json())
            if withdraw_request.account_id is not None:
                if not is_account_belong_to_current_user(withdraw_request.account_id):
                    return jsonify({"error": "Forbidden"}), 401
            transaction = withdraw(request=withdraw_request)
            return jsonify({"transaction": transaction.model_dump()}), 200
        except ValidationError as e:
            return parseValidationError(e, 400)
        except AccountNotFoundException as e:
            return jsonify({"error": str(e)}), 404
        
    @bp.route("/deposit", methods=["POST"])
    @jwt_required
    def handle_deposit():
        try:
            deposit_request = DepositRequest(**request.get_json())
            if deposit_request.account_id is not None:
                if not is_account_belong_to_current_user(deposit_request.account_id):
                    return jsonify({"error": "Forbidden"}), 401
            transaction = deposit(request=deposit_request)
            return jsonify({"transaction": transaction.model_dump()}), 200
        except ValidationError as e:
            return parseValidationError(e, 400)
        except AccountNotFoundException as e:
            return jsonify({"error": str(e)}), 404
        
    @bp.route("/transfer", methods=["POST"])
    @jwt_required
    def handle_transfer():
        try:
            transfer_request = TransferRequest(**request.get_json())
            if transfer_request.account_id is not None:
                if not is_account_belong_to_current_user(transfer_request.account_id):
                    return jsonify({"error": "Forbidden"}), 401
            transaction = transfer(request=transfer_request)
            return jsonify({"transaction": transaction.model_dump()}), 200
        except ValidationError as e:
            return parseValidationError(e, 400)
        except AccountNotFoundException as e:
            return jsonify({"error": str(e)}), 404

    @bp.route("/", methods=["GET"])
    @jwt_required
    def handle_get_transactions():
        try:
            current_user = get_jwt_identity()
            query = parse_transaction_query()
            transactions = db_get_transactions(query=query, current_user=current_user)
            return jsonify({"transactions": [transaction.model_dump() for transaction in transactions]}), 200
        except ValidationError as e:
            return e.errors(), 400
        except AccountsNotFoundException as e:
            return jsonify({"message": "no account found for the user"}), 404
        
    @bp.route("/<string:id>", methods=["GET"])
    def get_transaction(id:str):
        try:
            transaction = db_get_transaction(id)
            if not is_account_belong_to_current_user(transaction.account_id):
                return jsonify({"error": "Forbidden"}), 401
            return jsonify({"transaction": transaction.model_dump()}), 200
        except TransactionNotFoundException as e:
            return jsonify({"error": str(e)}), 404
    
    return bp
    

def parse_transaction_query() -> TransactionQuery:
    account_id = request.args.get("account_id")
    range_from = request.args.get("range_from")
    range_to = request.args.get("range_to")
    transaction_type = request.args.get("transaction_type")

    transaction_types: List[str] | None = None
    if transaction_type is not None:
        split = transaction_type.split(",")

        if len(split) > 0:
            while "" in split:
                split.remove("")

        if len(split) > 0:
            transaction_types = split
    
    
    return TransactionQuery(account_id=account_id, range_from=range_from, range_to=range_to, transaction_type=transaction_types)
