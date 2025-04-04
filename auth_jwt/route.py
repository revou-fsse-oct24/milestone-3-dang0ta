from functools import wraps
from flask import request, jsonify
from .tokens import is_valid_token
from .blacklist import is_blacklisted
from typing import Optional

def get_jwt_identity() -> Optional[str]:
    token = get_token()
    if not token:
        return None
    
    is_valid, payload = is_valid_token(token)
    if not is_valid:
        return None
    
    if "sub" not in payload:
        return None
    
    return payload["sub"]


def jwt_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = get_token()
        if token is None:
            return jsonify({"error": "Unauthorized"}), 401

        if is_blacklisted(token):
            return jsonify({"error": "Unauthorized"}), 401
        
        is_valid, payload = is_valid_token(token)
        if not is_valid:
            return jsonify({"error": str(payload)}), 401
        
        return f(*args, **kwargs)
    return decorator

def get_token()-> Optional[str]:
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None

    return parts[1]