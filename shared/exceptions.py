from flask import Response, jsonify
from pydantic import ValidationError

def parseValidationError(e:ValidationError, status: int) -> tuple[Response, int]:
    errors = e.errors()
    if not errors:
        return jsonify({"error": "Invalid account data"}), status
        
    fields = [field.get("loc", [])[0] if field.get("loc") else "unknown" for field in errors]
    fields_str = ", ".join(fields)
    return jsonify({"error": f"invalid fields: {fields_str}"}), status