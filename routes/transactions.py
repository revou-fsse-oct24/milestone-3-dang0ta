from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from auth_jwt import jwt_required, get_jwt_identity
from db.transactions import withdraw, deposit, transfer, get_transactions as db_get_transactions, get_transaction as db_get_transaction, TransactionNotFoundException, TransactionQuery
from db.accounts import AccountsNotFoundException
from models import Transaction, WithdrawRequest, DepositRequest, TransferRequest
from typing import List

def transaction_bp() -> Blueprint:
    bp = Blueprint("transactions", __name__, url_prefix="/transactions")

    @bp.route("/withdraw", methods=["POST"])
    @jwt_required
    def handle_withdraw():
        try:
            withdraw_request = WithdrawRequest(**request.get_json())
            transaction = withdraw(withdraw_request.account_id, withdraw_request.amount)
            return jsonify({"transaction": transaction.model_dump()}), 200
        except ValidationError as e:
            return e.errors(), 400
        
    @bp.route("/deposit", methods=["POST"])
    @jwt_required
    def handle_deposit():
        try:
            deposit_request = DepositRequest(**request.get_json())
            transaction = deposit(deposit_request.account_id, deposit_request.amount)
            return jsonify({"transaction": transaction.model_dump()}), 200
        except ValidationError as e:
            return e.errors(), 400
        
    @bp.route("/transfer", methods=["POST"])
    @jwt_required
    def handle_transfer():
        try:
            transfer_request = TransferRequest(**request.get_json())
            transaction = transfer(transfer_request.account_id, transfer_request.recipient_account_id, transfer_request.amount)
            return jsonify({"transaction": transaction.model_dump()}), 200
        except ValidationError as e:
            return e.errors(), 400  

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
            return jsonify({"transaction": transaction.model_dump()}), 200
        except TransactionNotFoundException as e:
            return jsonify({"message": "transaction can't be found"}), 404
    
    return bp
    
    

def create_transaction():
    try:
        current_user = get_jwt_identity()
        if current_user == None:
            return "Unauthorized",401
        
        transaction_request = Transaction(**request.get_json())
        match transaction_request.transaction_type.lower():
            case "withdraw":
                transaction = withdraw(transaction_request.account_id, transaction_request.amount)
                return jsonify({"transaction": transaction}), 200
            case "deposit":
                transaction = deposit(transaction_request.account_id, transaction_request.amount)
                return jsonify({"transaction": transaction}), 200
            case "transfer":
                transaction = transfer(account_id=transaction_request.account_id, recipient_account_id=transaction_request.recipient_account_id, amount=transaction_request.amount)
                return jsonify({"transaction": transaction}), 200
            case _:
                return jsonify({"message": "invalid transaction type"}), 400
    except ValidationError as e:
        return e.errors(), 400
    


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
