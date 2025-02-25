#MIT License
#
#Copyright (c) 2022 John Damilola, Leo Hsiang, Swarangi Gaurkar, Kritika Javali, Aaron Dias Barreto
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

'''routes.py is a file in deck folder that has all the functions defined that manipulate the deck. All CRUD functions are defined here.'''
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from datetime import datetime
import random

try:
    from .. import firebase
except ImportError:
    from __init__ import firebase


deck_bp = Blueprint('deck_bp', __name__)
db = firebase.database()

@deck_bp.route('/deck/<id>', methods=['GET'])
@cross_origin(supports_credentials=True)
def getdeck(id):
    '''This method fetches a specific deck by its ID.'''
    try:
        deck = db.child("deck").child(id).get()
        return jsonify(
            deck=deck.val(),
            message='Fetched deck successfully',
            status=200
        ), 200
    except Exception as e:
        return jsonify(
            decks=[],
            message=f"An error occurred: {e}",
            status=500
        ), 500

@deck_bp.route('/deck/all', methods=['GET'])
@cross_origin(supports_credentials=True)
def getdecks():
    '''Fetch all decks. Shows private decks for authenticated users and public decks for non-authenticated users.'''
    args = request.args
    localId = args.get('localId')
    try:
        decks = []
        # id_list = []
        if localId:
            user_decks = db.child("deck").order_by_child("userId").equal_to(localId).get()
            for deck in user_decks.each():
                obj = deck.val()
                obj['id'] = deck.key()
                cards = db.child("card").order_by_child("deckId").equal_to(deck.key()).get()
                obj['cards_count'] = len(cards.val()) if cards.val() else 0
                decks.append(obj)
        else:
            alldecks = db.child("deck").order_by_child("visibility").equal_to("public").get()
            for deck in alldecks.each():
                obj = deck.val()
                obj['id'] = deck.key()
                # id_list.append(deck.key())
                cards = db.child("card").order_by_child("deckId").equal_to(deck.key()).get()
                obj['cards_count'] = len(cards.val()) if cards.val() else 0
                decks.append(obj)
        # print(f"************ Deck id's are are {id_list[:200]}"). To remove test decks
        return jsonify(decks=decks, message='Fetching decks successfully', status=200), 200
    except Exception as e:
        return jsonify(decks=[], message=f"An error occurred {e}", status=500), 500

@deck_bp.route('/deck/create', methods=['POST'])
@cross_origin(supports_credentials=True)
def create():
    '''Create a new deck.'''
    try:
        data = request.get_json()
        localId = data['localId']
        title = data['title']
        description = data['description']
        visibility = data['visibility']
        
        db.child("deck").push({
            "userId": localId,
            "title": title,
            "description": description,
            "visibility": visibility,
            "cards_count": 0,
            "lastOpened": None
        })

        return jsonify(message='Create Deck Successful', status=201), 201
    except Exception as e:
        return jsonify(message=f'Create Deck Failed {e}', status=500), 500

@deck_bp.route('/deck/update/<id>', methods=['PATCH'])
@cross_origin(supports_credentials=True)
def update(id):
    '''Update an existing deck.'''
    try:
        data = request.get_json()
        localId = data['localId']
        title = data['title']
        description = data['description']
        visibility = data['visibility']

        db.child("deck").child(id).update({
            "userId": localId,
            "title": title,
            "description": description,
            "visibility": visibility
        })

        return jsonify(message='Update Deck Successful', status=201), 201
    except Exception as e:
        return jsonify(message=f'Update Deck Failed {e}', status=500), 500

@deck_bp.route('/deck/delete/<id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def delete(id):
    '''Delete a deck.'''
    try:
        db.child("deck").child(id).remove()
        return jsonify(message='Delete Deck Successful', status=200), 200
    except Exception as e:
        return jsonify(message=f'Delete Deck Failed {e}', status=500), 500

@deck_bp.route('/deck/updateLastOpened/<id>', methods=['PATCH'])
@cross_origin(supports_credentials=True)
def update_last_opened(id):
    '''Update the lastOpened timestamp when a deck is opened.'''
    try:
        current_time = datetime.utcnow().isoformat()
        db.child("deck").child(id).update({"lastOpened": current_time})
        return jsonify(message='Deck lastOpened updated successfully', status=200), 200
    except Exception as e:
        return jsonify(message=f'Failed to update lastOpened: {e}', status=500), 500

@deck_bp.route('/deck/streak/<id>', methods=['GET', 'PATCH'])
@cross_origin(supports_credentials=True)
def handle_streak(id):
    if request.method == 'GET':
        try:
            deck_data = db.child("deck").child(id).get()
            if not deck_data.val():
                return jsonify(message="Deck not found", status=404), 404

            streak = deck_data.val().get("streak", 0)  # Fetch the streak value
            return jsonify(streak=streak, status=200), 200
        except Exception as e:
            return jsonify(message=f"Error fetching streak: {e}", status=400), 400

    elif request.method == 'PATCH':
        try:
            data = request.get_json()  
            # print(f"Received request to update streak for deck {id} with data: {data}")

            deck_data = db.child("deck").child(id).get()
            if not deck_data.val():
                return jsonify(message="Deck not found", status=404), 404

            # Process the streak logic
            current_streak = deck_data.val().get("streak", 0)
            last_study_date = deck_data.val().get("lastOpened")

            today = datetime.now().date().isoformat()
            # today = (datetime.now().date()).replace(day=datetime.now().day + 1)

            if last_study_date == today:
                return jsonify(message="Streak already updated for today", streak=current_streak, status=200), 200
                    
            # print(f"Last study date: {last_study_date}, today: {today}")


            if last_study_date:
                last_date = datetime.fromisoformat(last_study_date).date()
                if (datetime.now().date() - last_date).days == 1:
                    current_streak += 1
                else:
                    current_streak = 1
            else:
                current_streak = 1

            db.child("deck").child(id).update({
                "streak": current_streak,
                "lastOpened": today
            })

            # print(f"Updated streak for deck {id}: {current_streak}")

            return jsonify(message="Streak updated", streak=current_streak, status=200), 200

        except Exception as e:
            print(f"Error updating streak for deck {id}: {e}")  
            return jsonify(message=f"Failed to update streak: {e}", status=400), 400
        
@deck_bp.route('/deck/goal/<id>', methods=['GET', 'PATCH'])
@cross_origin(supports_credentials=True)
def handle_goal(id):
    studyGoals = [
        "Study this deck for 20 minutes",
        "Add 5 new flashcards to this deck",
        "Take a quiz in this deck"
    ]  
    if (request.method == 'GET'):
        try:
            deck_data = db.child("deck").child(id).get()
            if not deck_data.val():
                return jsonify(message="Deck not found", status=404), 404

            today = datetime.now().date().isoformat()
            # today = (datetime.now().date()).replace(day=datetime.now().day + 3).isoformat()

            goal = deck_data.val().get("dailyGoal")
            goal_date = deck_data.val().get("goalDate")
            goal_completed = deck_data.val().get("goalCompleted", False)

            # Assign a new goal if it's a new day or goal doesn't exist
            if goal_date != today or not goal:
                new_goal = random.choice(studyGoals)
                
                # Assign a target based on the goal type
                target = 1
                if "Study this deck for 20 minutes" in new_goal:
                    target = 150  # 20 minutes (1200 seconds)
                elif "Add 5 new flashcards" in new_goal:
                    current_card_count = db.child("card").order_by_child("deckId").equal_to(id).get().val()
                    current_card_count = len(current_card_count) if current_card_count else 0

                    target = current_card_count + 5  # 5 flashcards
                elif "Take a quiz in this deck" in new_goal:
                    target = 1 # 1 quiz
                
                db.child("deck").child(id).update({
                    "dailyGoal": new_goal,
                    "goalDate": today,
                    "goalCompleted": False,
                    "goalProgress": 0,
                    "goalTarget": target
                })
                goal = new_goal
                goal_completed = False

            return jsonify(goal=goal, goalCompleted=goal_completed, status=200), 200
        except Exception as e:
            return jsonify(message=f"Error fetching goal: {e}", status=400), 400
    elif request.method == 'PATCH':
        """Marks the deck's goal as completed OR updates progress"""
        try:
            data = request.get_json()
            progress = data.get("progress", 1)  # Default to +1 progress
            
            print("recived patch with ", progress)

            deck_data = db.child("deck").child(id).get()
            if not deck_data.val():
                return jsonify(message="Deck not found", status=404), 404
            
            goal = deck_data.val().get("dailyGoal", "")
            
            print(goal)

            if data and "Study this deck for 20 minutes" in goal:
                goal_progress = deck_data.val().get("goalProgress", 0) + progress
            else:
                goal_progress = deck_data.val().get("goalProgress", 0) + progress
            goal_target = deck_data.val().get("goalTarget", 1)
            goal_completed = goal_progress >= goal_target
            
            print("goal progress: ", goal_progress)
            print("goal target: ", goal_target)
            print(goal_completed)

            db.child("deck").child(id).update({
                "goalProgress": goal_progress,
                "goalCompleted": goal_completed
            })

            return jsonify(message="Goal progress updated", goalProgress=goal_progress, goalCompleted=goal_completed, status=200), 200
        except Exception as e:
            return jsonify(message=f"Error updating goal: {e}", status=400), 400
        
@deck_bp.route('/deck/quizCompleted/<id>', methods=['PATCH'])
@cross_origin(supports_credentials=True)
def update_quiz_progress(id):
    '''Automatically update progress when a quiz is completed.'''
    try:
        deck_data = db.child("deck").child(id).get()
        if not deck_data.val():
            return jsonify(message="Deck not found", status=404), 404

        goal = deck_data.val().get("dailyGoal", "")
        goal_progress = deck_data.val().get("goalProgress", 0)
        goal_target = deck_data.val().get("goalTarget", 1)
        goal_completed = deck_data.val().get("goalCompleted", False)

        # If the goal is "Take a quiz", increase progress
        if "quiz" in goal.lower() and not goal_completed:
            goal_progress += 1
            goal_completed = goal_progress >= goal_target

        db.child("deck").child(id).update({
            "goalProgress": goal_progress,
            "goalCompleted": goal_completed
        })

        return jsonify(message="Quiz progress updated", goalProgress=goal_progress, goalCompleted=goal_completed, status=200), 200
    except Exception as e:
        return jsonify(message=f"Failed to update quiz progress: {e}", status=400), 400
    


@deck_bp.route('/deck/<deckId>/leaderboard', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_leaderboard(deckId):
    '''This endpoint fetches the leaderboard data for a specific deck.'''
    try:
        # Fetch leaderboard data for the given deck
        leaderboard_entries = db.child("leaderboard").child(deckId).get()
        leaderboard = []
        for entry in leaderboard_entries.each():
            data = entry.val()
            leaderboard.append({
                "userEmail": data.get("userEmail"),
                "correct": data.get("correct", 0),
                "incorrect": data.get("incorrect", 0),
                "lastAttempt": data.get("lastAttempt")
            })

        # Sort leaderboard by score (correct answers) then by last attempt (descending)
        leaderboard.sort(key=lambda x: (x["correct"], x["lastAttempt"]), reverse=True)

        return jsonify({
            "leaderboard": leaderboard,
            "message": "Leaderboard data fetched successfully",
            "status": 200
        }), 200
    except Exception as e:
        return jsonify({
            "leaderboard": [],
            "message": f"An error occurred: {e}",
            "status": 500
        }), 500
    
@deck_bp.route('/deck/<deck_id>/update-leaderboard', methods=['POST'])
@cross_origin(supports_credentials=True)
def update_leaderboard(deck_id):
    try:
        data = request.get_json()
        # Extract values from the request body
        user_id = data.get("userId")  # Get userId from request body
        user_email = data.get("userEmail")  # Keep for logging or notification
        correct = data.get("correct")
        incorrect = data.get("incorrect")

        if not user_id:
            return jsonify({"message": "User ID is required"}), 500  # Validate userId presence

        # Use user_id from request body to update the leaderboard
        leaderboard_ref = db.child("leaderboard").child(deck_id).child(user_id)
        leaderboard_ref.update({
            "userEmail": user_email,
            "correct": correct,
            "incorrect": incorrect,
            "lastAttempt": datetime.now().isoformat()
        })

        return jsonify({"message": "Leaderboard updated successfully"}), 200

    except Exception as e:
        return jsonify({"message": "Failed to update leaderboard", "error": str(e)}), 500
    
@deck_bp.route('/deck/<deckId>/user-score/<userId>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_user_score(deckId, userId):
    '''This endpoint fetches the user's score for a specific deck. If the user doesn't exist, return zero for all score values.'''
    try:
        # Fetch the user's leaderboard entry for the specified deck
        leaderboard_entry = db.child("leaderboard").child(deckId).child(userId).get()

        if leaderboard_entry.val() is not None:  # Check if the entry has data
            data = leaderboard_entry.val()  # Get the value of the entry
            score_data = {
                "correct": data.get("correct", 0),
                "incorrect": data.get("incorrect", 0),
            }
            return jsonify({
                "score": score_data,
                "message": "User score fetched successfully",
                "status": 200
            }), 200
        else:
            # Return zero for all score values if no entry exists
            return jsonify({
                "score": {
                    "correct": 0,
                    "incorrect": 0
                },
                "message": "No score found for the user, returning zeros.",
                "status": 200  # Not Found status, as the user has no scores yet
            }), 200

    except Exception as e:
        return jsonify({
            "message": f"An error occurred: {e}",
            "status": 500
        }), 500

# @deck_bp.route('/deck/<id>/last-opened', methods=['PATCH'])
# @cross_origin(supports_credentials=True)
# def update_last_opened_deck(id):
#     try:
#         data = request.get_json()
#         last_opened_at = data.get('lastOpenedAt')
        
#         db.child("deck").child(id).update({
#             "lastOpenedAt": last_opened_at
#         })

#         return jsonify(
#             message='Last opened time updated successfully',
#             status=200
#         ), 200
#     except Exception as e:
#         return jsonify(
#             message=f"Failed to update last opened time: {e}",
#             status=500
#         ), 500