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
  print("token", token)
  if not token:
    return jsonify({'message': 'Token is missing'}), 401
  try:
    decoded_token = auth.get_account_info(token)
    print("decoded_token", decoded_token)
    # Token is valid
    return decoded_token.get('users')[0].get('localId')
  except Exception as e:
    # Token is invalid
    return jsonify({'message': 'Invalid token'}), 403


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


def user_owns_folder(uid, folder_id):
  '''helper for has_folder_rights. returns json error message if error, otherwise True'''
  try:
    folder_snapshot = db.child("folder").child(folder_id).get().val()
  except Exception as e:
    return jsonify({'message': str(e)}), 500
  if folder_snapshot is None:
    return jsonify({"message": "Folder not found"}), 404
  print("folder_snapshot", folder_snapshot)
  if folder_snapshot.get('userId') != uid:
    return jsonify({"message": "Unauthorized"}), 401

  return True

def user_owns_deck(uid, deck_id):
  '''helper for has_deck_rights. returns json error message if error, otherwise True'''
  try:
    deck_snapshot = db.child("deck").child(deck_id).get().val()
  except Exception as e:
    return jsonify({'message': str(e)}), 500

  if deck_snapshot is None:
    return jsonify({"message": "Deck not found"}), 404
  if deck_snapshot.get('userId') != uid:
    return jsonify({"message": "Unauthorized"}), 401

  return True


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

    response = user_owns_folder(uid, kwargs.get('folder_id', None))
    if response:
      return f(*args, **kwargs)
    else:
      return response

  return decorated

def deck_visible_helper(deck_id, uid):
  '''Helper function for deck_is_visible'''

  deck_snapshot = db.child("deck").child(deck_id).get().val()
  if deck_snapshot is None:
    return jsonify({"message": "Deck not found"}), 404
  if deck_snapshot.get('userId') != uid:
    if deck_snapshot.get('visibility') != 'public':
      return jsonify({"message": "Unauthorized"}), 401

  return True

def deck_is_visible(f):
  """this function is a decorator that checks if a user can view a deck."""

  @wraps(f)
  def decorated(*args, **kwargs):
    uid = get_user_id_from_request()
    if type(uid) is not str:
      return uid

    response = deck_visible_helper(kwargs.get('deck_id', None), uid)
    if not response:
      return response

    return f(*args, **kwargs)

  return decorated

def has_deck_rights(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    uid = get_user_id_from_request()
    if type(uid) is not str:
      return uid

    deck_snapshot = db.child("deck").child(kwargs.get('deck_id', None)).get().val()
    if deck_snapshot is None:
      return jsonify({"message": "Deck not found"}), 404
    if deck_snapshot.get('userId') != uid:
      return jsonify({"message": "Unauthorized"}), 401

    return f(*args, **kwargs)
  return decorated_function

def has_folder_and_deck_rights(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if request.method == 'POST':
      uid = get_user_id_from_request()
      data = request.get_json()

      folder_response = user_owns_folder(uid, data.get('folderId'))
      if not folder_response:
        return folder_response

      deck_response = user_owns_deck(uid, data.get('deckId'))
      if not deck_response:
        return deck_response
    else:
      return jsonify({'message': 'Method not allowed'}), 405

    return f(*args, **kwargs)

  return decorated_function