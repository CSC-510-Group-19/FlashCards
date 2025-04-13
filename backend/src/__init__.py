from functools import wraps
from flask import Flask, jsonify, request

import pyrebase

config = {
  'apiKey': "AIzaSyAPXpHYZpD5DNjsg6XAEhTVA5V9kA5rNWY",
  'authDomain': "flashcards-93088.firebaseapp.com",
  'databaseURL': "https://flashcards-93088-default-rtdb.firebaseio.com",
  'projectId': "flashcards-93088",
  'storageBucket': "flashcards-93088.firebasestorage.app",
  'messagingSenderId': "457073208752",
  'appId': "457073208752:web:0c6e9eaea7740d4a387a75"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()


def get_user_id_from_request():
  token = request.headers.get('Authorization')
  if not token:
    return jsonify({'message': 'No Authorization Token found'}), 401

  # token validator
  try:
    decoded_token = auth.verify_id_token(token)
    return jsonify(
      uid=decoded_token['uid']
    )
    # Token is valid
  except auth.InvalidIdTokenError as e:
    # Token is invalid
    return jsonify({"uid": None, "message": "Invalid token: " + e.message}), 401
  except auth.UserDisabledError as e:
    # Token belongs to a disabled user record
    return jsonify({"uid": None, "Message": "User disabled: " + e.message}), 401

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