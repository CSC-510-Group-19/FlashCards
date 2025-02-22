from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from datetime import datetime

try:
    from .. import firebase
except ImportError:
    from __init__ import firebase

user_bp = Blueprint('user_bp', __name__)
db = firebase.database()

@user_bp.route('/user/<user_id>/streak', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_streak(user_id):
    '''get the user's current streak'''
    try: 
        user_data = db.child("users").child(user_id).get()
        streak = user_data.val().get("streak", 0) if user_data.val() else 0
        return jsonify(streak=streak, status=200), 200
    except Exception as e:
        return jsonify(message=f"Error fetching streak: {e}", status=400), 400
                    
@user_bp.route('/user/<user_id>/update-streak', methods=['PATCH'])
@cross_origin(supports_credentials=True)
def update_streak(user_id):
    '''Update streak after the user accesses a deck'''
    try: 
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