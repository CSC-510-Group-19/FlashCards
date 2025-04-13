from firebase_admin import auth
from flask import jsonify, Blueprint


def get_user_id_from_request(request):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'No Authorization Token found'}), 401

    # token validator
    try:
        decoded_token = auth.verify_id_token(token)
        return jsonify(
            uid= decoded_token['uid']
        )
        # Token is valid
    except auth.InvalidIdTokenError as e:
        # Token is invalid
        return jsonify({"uid": None, "message": "Invalid token: " + e.message}), 401
    except auth.UserDisabledError as e:
        # Token belongs to a disabled user record
        return jsonify({"uid": None, "Message": "User disabled: " + e.message}), 401