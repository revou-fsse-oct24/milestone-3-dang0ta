from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from auth_jwt import create_access_token, create_refresh_token, is_valid_token, add_to_blacklist
from auth import AuthRepository, WrongCredentialException, UserNotFoundException


def auth_bp(auth: AuthRepository) -> Blueprint:
    bp = Blueprint("auth", __name__, url_prefix="/auth")

    @bp.route("/login", methods=["POST"])
    def login():
        try:
            data = request.json
            email = data.get("email")
            password = data.get("password")

            user_id = auth.authenticate(email, password)
            if user_id == None:
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
    def logout():
        token = request.json.get('access_token')
        if token:
            add_to_blacklist(token)
        return jsonify({'message': 'Logged out successfully'}), 200
        
    return bp