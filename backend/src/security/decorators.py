from functools import wraps

from firebase_admin import auth
from flask import request, jsonify, Blueprint

from backend.src.auth.utils import get_user_id_from_request

security_decorators_bp = Blueprint('security_decorators_bp', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        uid_json = get_user_id_from_request(request)
        if uid_json.get('uid') is None:
            return uid_json
        return f(*args, **kwargs)

    return decorated


def has_folder_rights(f):
    '''this function is a decorator that checks if the authorization token in the header
    corresponds to the user id in the decorated function parameters. For this to work as intended
    the decorated function must have the user id must have the rights to modify the folder corresponding to folder id in a parameter folder_Id.'''
    @wraps(f)
    def decorated(*args, **kwargs):
        uid_json = get_user_id_from_request(request)
        if uid_json.get('uid') is None:
            return uid_json
        uid = uid_json.get('uid')

        folder_snapshot = db.child("folder").child(kwargs.get('folder_id', None)).get()
        if not folder_snapshot.exists:
            return jsonify({"message": "Folder not found"}), 404

        if folder_snapshot.get().val().userId != uid:
            return jsonify({"message": "Unauthorized"}), 401

        return f(*args, **kwargs)

    return decorated