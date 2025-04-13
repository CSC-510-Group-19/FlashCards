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
  print('get user id token')
  print(token)
  if not token:
    return jsonify({'message': 'No Authorization Token found'}), 401

  # token validator
  try:
    user = auth.get_account_info(token)
    print('valid token2')
    return user
    # Token is valid
  except auth.InvalidIdTokenError as e:
    # Token is invalid
    return jsonify({"uid": None, "message": "Invalid token"}), 401
  except auth.UserDisabledError as e:
    # Token belongs to a disabled user record
    return jsonify({"uid": None, "Message": "User disabled"}), 401


def token_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    # try:
    #     uid = get_user_id_from_request(request)
    #     return uid_json.get('uid')
    # except BadRequest:
    #     return jsonify({'error': 'Invalid JSON'}), 400
    #
    # if uid_json['uid'] is None:
    #     return uid_json
    uid = get_user_id_from_request()
    print("token required uid ")
    print(uid)

    if type(uid) is not str:
      return uid

    return f(*args, **kwargs)

  return decorated


def has_folder_rights(f):
  """this function is a decorator that checks if the authorization token in the header
  corresponds to the user id in the decorated function parameters. For this to work as intended
  the decorated function must have the user id must have the rights to modify the folder corresponding
  to folder id in a parameter folder_Id."""

  @wraps(f)
  def decorated(*args, **kwargs):
    uid = get_user_id_from_request()
    if type(uid) is not str:
      return uid

    folder_snapshot = db.child("folder").child(kwargs.get('folder_id', None)).get()
    if not folder_snapshot.exists:
      return jsonify({"message": "Folder not found"}), 404

    if folder_snapshot.get().val().userId != uid:
      return jsonify({"message": "Unauthorized"}), 401

    return f(*args, **kwargs)

  return decorated