from flask import has_request_context, g, abort
from auth_jwt import get_jwt_identity
from db.users import get_user
from functools import wraps
from models import UserInformation
from typing import Optional

def role_required(*roles: tuple[str]):
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            if not roles or len(roles) == 0:
                return func(*args, **kwargs)
            
            current_user = load_current_user()
            if current_user is None:
                abort(403)
            
            for role in roles:
                if role not in current_user.roles:
                    abort(403)

            return func(*args, **kwargs)
        return decorator
    return wrapper


def is_account_belong_to_current_user(account_id: str) -> bool:
    current_user = load_current_user()
    if current_user is None:
        return False

    return account_id in [account.id for account in current_user.accounts]

def load_current_user() -> Optional[UserInformation]:
    if has_request_context():
        if "_login_user" not in g:
            current_user_id = get_jwt_identity()
            if current_user_id is None:
                return None

            user =  get_user(current_user_id)
            if user is None:
                return None
            g._login_user = user

        return g._login_user
    return None