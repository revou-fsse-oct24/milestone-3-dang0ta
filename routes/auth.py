from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from auth_jwt import create_access_token, create_refresh_token, is_valid_token, add_to_blacklist, jwt_required, get_token
from db.credentials import get_and_compare_hash, WrongCredentialException, UserNotFoundException

def auth_bp() -> Blueprint:
    bp = Blueprint("auth", __name__, url_prefix="/auth")

    @bp.route("/login", methods=["POST"])
    def login():
        try:
            data = request.json
            email = data.get("email")
            password = data.get("password")

            user_id = get_and_compare_hash(email_address=email, password=password)
            if user_id is None:
                raise UserNotFoundException(email)
            
            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)
            return jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 200
        except ValidationError as e:
            return e.errors(), 400
        except WrongCredentialException as e:
            # TODO: log the email
            return str(e), 403
        except UserNotFoundException as e:
            # TODO: log the email
            return str(e), 403
        
    @bp.route('/refresh', methods=["POST"])
    def refresh():
        token = request.json.get('refresh_token')
        is_valid, payload = is_valid_token(token)
        if not is_valid or payload.get('type') != 'refresh':
            return jsonify({'message': 'Invalid or expired refresh token'}), 401
        
        new_access_token = create_access_token(identity=payload['sub'])
        return jsonify({'access_token': new_access_token}), 200
        
    @bp.route("/logout")
    @jwt_required
    def logout():
        token = get_token()
        if token is not None:
            add_to_blacklist(token)
        return jsonify({'message': 'Logged out successfully'}), 200
        
    return bp