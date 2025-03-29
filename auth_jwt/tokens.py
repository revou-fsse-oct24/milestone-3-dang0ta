from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from datetime import timedelta, datetime, timezone
from flask import current_app
from config import jwt_secret, jwt_algorithm
from exceptions import ConfigurationError
from typing import Dict

if not jwt_secret:
    raise ConfigurationError("JWT_SECRET is not set")

if not jwt_algorithm:
    raise ConfigurationError("JWT_ALGORITHM is not set")

def create_access_token(identity:int, expires_delta=None) -> str:
    if not expires_delta:
        expires_delta = timedelta(hours=1) # token is expired in 1 hour by default.

    payload = {
        'sub': str(identity),
        'exp': datetime.now(timezone.utc) + expires_delta,
        'iat': datetime.now(timezone.utc),  # created at
        'type': 'access' # OAuth 2.0 common custom claim, indicates access token.
    }

    token = encode(payload, jwt_secret, algorithm=jwt_algorithm)
    return token

def create_refresh_token(identity: str) -> str:
    payload = {
        'sub': identity,
        'exp': datetime.now(timezone.utc) + timedelta(days=7), # refresh token usually expires at much longer time duration.
        'iat': datetime.now(timezone.utc),  # created at
        'type': 'refresh', # OAuth 2.0 common custom claim, indicates refresh token. 
    }

    token = encode(payload, jwt_secret, algorithm=jwt_algorithm)
    return token

def decode_token(token: str) -> Dict:
    try:
        payload = decode(token, jwt_secret, algorithms=jwt_algorithm)
        return payload
    except ExpiredSignatureError:
        return {'error': 'Token Expired'}
    except InvalidTokenError:
        return {'error': 'Invalid Token'}
    
def is_valid_token(token: str):
    payload = decode_token(token=token)
    if "error" in payload:
        return False, payload["error"]
    return True, payload    