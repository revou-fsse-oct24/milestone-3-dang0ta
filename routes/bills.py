from flask import Blueprint, request, jsonify
from auth_jwt import jwt_required, get_jwt_identity
from pydantic import ValidationError
from models import CreateBillRequest, QueryBillsRequest, UpdateBillRequest
from shared.exceptions import parseValidationError
from db.bills import create_bill as db_create_bill
from db.bills import get_bills as db_get_bills
from db.bills import get_bill as db_get_bill
from db.bills import update_bill as db_update_bill
from db.bills import delete_bill as db_delete_bill
from db.bills import BillNotFoundException

def bills_bp() -> Blueprint:
    bp = Blueprint("bills", __name__, url_prefix="/bills")
    @bp.route("/", methods=["POST", "GET"])
    @jwt_required
    def handle_bills():
        match request.method:
            case "POST":
                return create_bills()
            case "GET":
                return get_bills()

    @bp.route("/<string:id>", methods=["PUT", "GET", "DELETE"])
    @jwt_required
    def handle_bill(id:str):
        match request.method:
            case "PUT":
                return update_bill(id)
            case "GET":
                return get_bill(id)
            case "DELETE":
                return delete_bill(id)

    
    return bp

def create_bills():
    try:
        # TODO: perform RBAC here
        current_user = get_jwt_identity()
        req = CreateBillRequest(**request.get_json())
        bill = db_create_bill(user_id=current_user, request=req)
        return jsonify({"bill": bill.model_dump()}), 200
    except ValidationError as e:
        if e.title == "CreateBillRequest":
            return parseValidationError(e, 400)
        return jsonify({"error": "the server responded with invalid data"}), 500


def get_bills():
    try:
        # TODO: perform RBAC here
        current_user = get_jwt_identity()
        req = QueryBillsRequest(**request.get_json())
        bills = db_get_bills(user_id=current_user, request=req)
        return jsonify({"bills": [bill.model_dump() for bill in bills]}), 200
    except ValidationError as e:
        if e.title == "QueryBillRequest":
            return parseValidationError(e, 400)
        return jsonify({"error": "the server responded with invalid data"}), 500

def update_bill(id: str):
    try:
        # TODO: perform RBAC here
        req = UpdateBillRequest(**request.get_json())
        bill = db_update_bill(bill_id=id, request=req)
        return jsonify({"bill": bill.model_dump()}), 200
    except ValidationError as e:
        if e.title == "QueryBillRequest":
            return parseValidationError(e, 400)
        return jsonify({"error": "the server responded with invalid data"}), 500
    except BillNotFoundException as e:
        return jsonify({"error": str(e)}), 404

def get_bill(id: str):
    try:
        # TODO: perform RBAC here
        bill = db_get_bill(bill_id=id)
        return jsonify({"bill": bill.model_dump()}), 200
    except ValidationError as e:
        return jsonify({"error": "the server responded with invalid data"}), 500
    except BillNotFoundException as e:
        return jsonify({"error": str(e)}), 404

def delete_bill(id: str):
    try:
        # TODO: perform RBAC here
        db_delete_bill(bill_id=id)
        return jsonify({"status": "deleted"}), 200
    except BillNotFoundException as e:
        return jsonify({"error": str(e)}), 404