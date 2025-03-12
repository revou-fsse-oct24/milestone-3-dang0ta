from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from auth_jwt import jwt_required, get_jwt_identity
from db import TransactionRepository, TransactionQuery, NewTransactionRequest

def transaction_bp(transactions: TransactionRepository) -> Blueprint:
    bp = Blueprint("transactions", __name__, url_prefix="/transactions")

    @bp.route("/", methods=["GET", "POST"])
    @jwt_required
    def handle_root_transaction():
         match request.method:
              case "GET":
                   return get_transactions(transactions)
              case "POST":
                   return create_transaction(transactions)
              case _:
                 return "Method not allowed", 405
        
    @bp.route("/<string:id>", methods=["GET"])
    def get_transaction(id:str):
        transaction = transactions.find_by_id(id)
        if transaction == None:
            return "transaction can't be found", 404

        return jsonify({"transaction": transaction}), 200
    
    return bp
    

def get_transactions(transactions: TransactionRepository):
    try:
        current_user = get_jwt_identity()
        if current_user == None:
            return "Unauthorized", 401
        
        query = TransactionQuery()
        if not request.content_length == None and request.content_length > 0:
            query = TransactionQuery(**request.get_json())

        user_transactions = transactions.query_transaction(user_id=current_user, query=query)
        return jsonify({"transactions": list(user_transactions)}), 200
    except ValidationError as e:
        return e.errors(), 400

def create_transaction(transactions: TransactionRepository):
    try:
        current_user = get_jwt_identity()
        if current_user == None:
            return "Unauthorized",401
        
        transaction_request = NewTransactionRequest(**request.get_json())
        created_transaction = transactions.create(transaction_request.create_transaction(user_id=current_user))
        return jsonify({"transaction": created_transaction}), 201
    except ValidationError as e:
        return e.errors(), 400