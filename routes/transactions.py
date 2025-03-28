from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from auth_jwt import jwt_required, get_jwt_identity
from db.transactions import withdraw, deposit, transfer, get_transactions as db_get_transactions, get_transaction as db_get_transaction, TransactionNotFoundException
from db.accounts import AccountNotFoundException, AccountsNotFoundException
from models import Transaction, WithdrawRequest, DepositRequest, TransferRequest

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

    @bp.route("/")
    @jwt_required
    def handle_root_transaction():
        try:
            current_user = get_jwt_identity()
            if current_user == None:
                return "Unauthorized", 401
            
            transactions = db_get_transactions(account_id=current_user)
            return jsonify({"transactions": list(transactions)}), 200
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