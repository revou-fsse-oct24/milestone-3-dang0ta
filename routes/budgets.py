from flask import Blueprint, request, jsonify
from auth_jwt import jwt_required, get_jwt_identity
from models import CreateBudgetRequest, UpdateBudgetRequest
from pydantic import ValidationError
from shared.exceptions import parseValidationError
from db.budgets import create_budget as db_create_budget
from db.budgets import get_budgets as db_get_budgets
from db.budgets import update_budget as db_update_budget
from db.budgets import delete_budget as db_delete_budget
from db.budgets import get_budget as db_get_budget
from db.budgets import BudgetsNotFoundException, BudgetNotFoundException

def budget_bp() -> Blueprint:
    bp = Blueprint("budgets", __name__, url_prefix="/budgets")
    @bp.route("/", methods=["POST", "GET"])
    @jwt_required
    def handle_budgets():
        match request.method:
            case "POST":
                return create_budget()
            case "GET":
                return get_budgets()
            
    @bp.route("/<string:id>", methods=["GET", "PUT", "DELETE"])
    @jwt_required
    def handle_budget(id: str):
        match request.method:
            case "GET":
                return get_budget(id)
            case "PUT":
                return update_budget(id)
            case "DELETE":
                return delete_budget(id)

    return bp

def create_budget():
    try:
        current_user = get_jwt_identity()
        req = CreateBudgetRequest(**request.get_json())
        res = db_create_budget(user_id=current_user, request=req)
        return jsonify({"budget": res.model_dump()}), 200
    except ValidationError as e:
        return parseValidationError(e, 400)

def get_budgets():
    try:
        current_user = get_jwt_identity()
        budgets = db_get_budgets(user_id=current_user)
        return jsonify({"budgets": [budget.model_dump() for budget in budgets]})
    except ValidationError:
        return jsonify({"error": "the server responded with invalid budget"}), 500
    except BudgetsNotFoundException as e:
        return jsonify({"error": str(e)}), 404
    
def get_budget(id: str):
    try:
        budget =  db_get_budget(id)
        return jsonify({"budget": budget.model_dump()})
    except BudgetNotFoundException as e:
        return jsonify({"error": str(e)}), 404
    
    
def update_budget(id: str):
    try:
        req = UpdateBudgetRequest(**request.get_json())
        res = db_update_budget(budget_id=id, request=req)
        return jsonify({"budget": res.model_dump()})
    except ValidationError as e:
        if e.title == "UpdateBudgetRequest":
            return parseValidationError(e, 400)
        return jsonify({"error": "the server responded with invalid data"}), 500
    except BudgetNotFoundException as e:
        return jsonify({"error": str(e)}), 404
    
def delete_budget(id: str):
    try:
        db_delete_budget(budget_id=id)
        return jsonify({"result": "deleted"})
    except BudgetNotFoundException as e:
        return jsonify({"error": str(e)}), 404