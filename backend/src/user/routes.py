from firebase_admin import auth
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from datetime import datetime

from ..api import token_required

try:
    from .. import firebase
except ImportError:
    from __init__ import firebase

user_bp = Blueprint('user_bp', __name__)
db = firebase.database()

@user_bp.route('/user/<user_id>/streak', methods=['GET'])
@cross_origin(supports_credentials=True)
@token_required
def get_streak(user_id):
    '''Get the user's current streak'''
    try:
        # Get token from request headers
        id_token = request.headers.get("Authorization")
        if not id_token:
            return jsonify(message="Missing authentication token", status=401), 401
        
        # Verify Firebase ID token
        decoded_token = auth.verify_id_token(id_token.replace("Bearer ", ""))
        if decoded_token["uid"] != user_id:
            return jsonify(message="Unauthorized access", status=403), 403
        
        # Fetch user streak from Firebase
        user_data = db.child("users").child(user_id).get()
        streak = user_data.val().get("streak", 0) if user_data.val() else 0
        return jsonify(streak=streak, status=200), 200
    
    except Exception as e:
        return jsonify(message=f"Error fetching streak: {e}", status=400), 400

# @user_bp.route('/user/<user_id>/streak', methods=['GET'])
# @cross_origin(supports_credentials=True)
# def get_streak(user_id):
#     '''get the user's current streak'''
#     try: 
#         print(f"Fetching streak for user: {user_id}")  # Debug log

#         user_data = db.child("users").child(user_id).get()

#         print(f"Firebase response: {user_data.val()}")  # Print the Firebase data
#         if not user_data.val():
#             return jsonify(message=f"User {user_id} not found in database", status=404), 404
        
#         streak = user_data.val().get("streak", 0) if user_data.val() else 0
        
#         print(f"User {user_id} has a streak of {streak}")

#         return jsonify(streak=streak, status=200), 200
#     except Exception as e:
#         return jsonify(message=f"Error fetching streak: {e}", status=400), 400
                    
@user_bp.route('/user/<user_id>/update-streak', methods=['PATCH'])
@cross_origin(supports_credentials=True)
@token_required
def update_streak(user_id):
    '''Update streak after the user accesses a deck'''
    try:
        token = request.headers.get("Authorization");
        if token:
            decoded_token = auth.verify_id_token(token);
            if decoded_token["uid"] != user_id:
                return jsonify(message="Unauthorized access", status=403), 403

        user_data = db.child("users").child(user_id).get()
        current_streak = user_data.val().get("streak", 0) if user_data.val() else 0
        last_study_date = user_data.val().get("lastStudyDate")
        
        today = datetime.now().date().isoformat()
        
        if last_study_date == today:
            return jsonify(message="Streak already updated for today", streak=current_streak, status=200), 200
        
        if last_study_date:
            last_date = datetime.fromisoformat(last_study_date).date()
            if (datetime.now().date() - last_date).days == 1: 
                current_streak += 1 
            else:
                current_streak = 1
        else:
            current_streak = 1
            
        db.child("users").child(user_id).update({
            "streak": current_streak,
            "lastStudyDate" : today
        })
        
        return jsonify(message="Streak updated", streak=current_streak, status=200), 200
    except Exception as e:
        return jsonify(message=f"Failed to update streak: {e}", status=400), 400