from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from datetime import timedelta, datetime, timezone
from flask import current_app
from typing import Dict

def create_access_token(identity:str, expires_delta=None) -> str:
    if not expires_delta:
        expires_delta = timedelta(hours=1) # token is expired in 1 hour by default.

    payload = {
        'sub': identity,
        'exp': datetime.now(timezone.utc) + expires_delta,
        'iat': datetime.now(timezone.utc),  # created at
        'type': 'access' # OAuth 2.0 common custom claim, indicates access token.
    }

    token = encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')
    return token

def create_refresh_token(identity: str) -> str:
    payload = {
        'sub': identity,
        'exp': datetime.now(timezone.utc) + timedelta(days=7), # refresh token usually expires at much longer time duration.
        'iat': datetime.now(timezone.utc),  # created at
        'type': 'refresh', # OAuth 2.0 common custom claim, indicates refresh token. 
    }

    token = encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')
    return token

def decode_token(token: str) -> Dict:
    try:
        payload = decode(token, current_app.config['JWT_SECRET'], algorithms='HS256')
        return payload
    except ExpiredSignatureError:
        return {'error', 'Token Expired'}
    except InvalidTokenError:
        return {'error': 'Invalid Token'}
    
def is_valid_token(token: str):
    payload = decode_token(token=token)
    if "error" in payload:
        return False, payload["error"]
    return True, payload