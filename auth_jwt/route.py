from functools import wraps
from flask import request
from .tokens import is_valid_token
from .blacklist import is_blacklisted
from typing import Optional

def get_jwt_identity() -> Optional[str]:
    token = _get_token()
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
        token = _get_token()
        if token is None:
            return "Unauthorized", 401

        if is_blacklisted(token):
            return "Unauthorized", 401
        
        is_valid, payload = is_valid_token(token)
        if not is_valid:
            return str(payload), 401
        
        return f(*args, **kwargs)
    return decorator

def _get_token()-> Optional[str]:
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None

    return parts[1]