 # MIT License
#
# Copyright (c) 2022 John Damilola, Leo Hsiang, Swarangi Gaurkar, Kritika Javali, Aaron Dias Barreto
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

'''routes.py is a file in the folder folder that has all the functions defined that manipulate folders. All CRUD functions are defined here.'''
from flask import Blueprint, jsonify, request # type: ignore
from flask_cors import cross_origin # type: ignore
# from __init__ import firebase

try:
    from .. import db, firebase, token_required, get_user_id_from_request, has_folder_rights, has_folder_and_deck_rights
except ImportError:
    from __init__ import db, firebase, token_required, get_user_id_from_request, has_folder_rights, has_folder_and_deck_rights
    
folder_bp = Blueprint(
    'folder_bp', __name__
)

db = firebase.database()

@folder_bp.route('/folder/<folder_id>', methods=['GET'])
@cross_origin(supports_credentials=True)
@has_folder_rights
def getfolder(folder_id):
    '''This method is called when we want to fetch one of the folders by folder ID'''
    try:
        folder = db.child("folder").child(folder_id).get()
        return jsonify(
            folder=folder.val(),
            message='Fetched folder successfully',
            status=200
        ), 200
    except Exception as e:
        return jsonify(
            folder={},
            message=f"An error occurred: {e}",
            status=500
        ), 500


@folder_bp.route('/folders/all', methods=['GET'])
@cross_origin(supports_credentials=True)
@token_required
def getfolders():
    '''This method is called when we want to fetch all folders for a specific user'''
    userId = get_user_id_from_request()
    try:
        #db.child("folder_deck").order_by_child("folderId").equal_to(folder_id).get()['progress']
        user_folders = db.child("folder").order_by_child("userId").equal_to(userId).get()
        folders = []
        for folder in user_folders.each():
            obj = folder.val()
            obj['id'] = folder.key()
            decks = db.child("folder_deck").order_by_child("folderId").equal_to(folder.key()).get()
            obj['decks'] = []
            if decks.each():
                for deck in decks.each():
                    deck_obj = deck.val()
                    deck_obj['id'] = deck.key()
                    obj['decks'].append(deck_obj)

            obj['decks_count'] = len(obj['decks'])
            folders.append(obj)
        
        return jsonify(
            folders=folders,
            message='Fetched folders successfully',
            status=200
        ), 200
    except Exception as e:
        return jsonify(
            folders=[],
            message=f"An error occurred: {e}",
            status=500
        ), 500


@folder_bp.route('/folder/create', methods=['POST'])
@cross_origin(supports_credentials=True)
@token_required
def createfolder():
    try:
        data = request.get_json()
        print("data", data)
        folder_name = data['name']
        user_id = data['userId']

        folder_ref = db.child("folder").push({
            "name": folder_name,
            "userId": user_id,
            "addess": 0
        })
        new_folder_id = folder_ref['name']  # Retrieve auto-generated ID
        print("progress is 0?")
        return jsonify(
            folder={
                "id": new_folder_id,
                "name": folder_name,
                "decks": [],
                "progress": 0
            },
            message='Folder created successfully',
            status=201
        ), 201
    except Exception as e:
        return jsonify(
            message=f"Failed to create folder: {e}",
            status=500
        ), 500

@folder_bp.route('/folders/all/update', methods=['POST'])
@cross_origin(supports_credentials=True)
def updatefolders():
    '''This method is called when we want to fetch all folders for a specific user'''
    data = request.get_json()
        # Extract values from the request body
    userId = data.get("userId") 
    try:
        user_folders = db.child("folder").order_by_child("userId").equal_to(userId).get()
        folders = []
        for folder in user_folders.each():
            obj = folder.val()
            obj['id'] = folder.key()
            obj['decks'] = []
            print(obj['id'])
            updatefolder_progress(obj['id'])

            obj['decks_count'] = len(obj['decks'])
            # folders.append(obj)
        
        return jsonify(
            folders=folders,
            message='Updated folders successfully',
            status=200
        ), 200
    except Exception as e:
        return jsonify(
            folders=[],
            message=f"An error occurred: {e}",
            status=500
        ), 500

@folder_bp.route('/folder/update/<folder_id>', methods=['PATCH'])
@cross_origin(supports_credentials=True)
@has_folder_rights
def updatefolder(folder_id):
    '''This method is called when the user wants to update a folder's name.'''
    try:
        data = request.get_json()
        folder_name = data.get('name')

        db.child("folder").child(folder_id).update({
            "name": folder_name
        })

        return jsonify(
            message='Folder updated successfully',
            status=201
        ), 201
    except Exception as e:
        return jsonify(
            message=f"Failed to update folder: {e}",
            status=500
        ), 500
# --------------CHANGED-----------------
@folder_bp.route('/folder/update-progress/<id>', methods=['PATCH'])
@cross_origin(supports_credentials=True)
def updatefolder_progress(folder_id):
    '''This method is called when a quiz is taken and a folder's progress bar should update.'''
    try:
        print('******')
        deck_list = []
        folder_deck_ref = db.child("folder_deck").order_by_child("folderId").equal_to(folder_id).get()
        for fd in folder_deck_ref.each():
            if fd.val().get('deckId') is None:
                continue
            deck_list.append(fd.val().get('deckId'))
        print(deck_list)
        # folder_obj = db.child("folder_deck").order_by_child("folderId").equal_to(folder_id).get()
        # deck_list = []
        # for folders in folder_obj.each():
        #     obj = folders.val()
        #     obj['id'] = folders.key()  # Optional: if you need the deck ID
        #     deck_list.append(obj["id"])
        # print("deck_list", deck_list)
        # print(len(deck_list))
        deck_list_length = len(deck_list)
        total = 0
        for deck in deck_list:
            deck_obj = db.child("deck").child(deck).get()
            print(deck_obj.val())
            # get_user_score(deckId, userId)
            deck_progress = deck_obj.val()["goalProgress"]
            print("deck_progress " + str(deck_progress))
            total = total + deck_progress
            print("new total: " + str(total))
        
        print("what happens now")
        folder_progress = 0
        print("what of the folder progress")
        # print("length of deck: " + len(deck_list))
        if(deck_list_length > 0):
            print('inside')
            folder_progress = total / len(deck_list)
        print("folder name " +  str(folder_id) + " folder progress " + str(folder_progress))

        # TODO: Check that db calls are made correctly
        # db.child("folder_deck").child(folder_id).update({
        #     "progress": folder_progress
        # })

        # db.child("folder").child(folder_id).update({
        #     "progress": folder_progress
        # })
        

        print("folder progress stored: " + str(db.child("folder_deck").order_by_child("folderId").equal_to(folder_id).get()['progress']))
        print("folder progress stored: " + str(db.child("folder").order_by_child("folderId").equal_to(folder_id).get()['progress']))

        return jsonify(
            message='Folder Progress updated successfully',
            status=201
        ), 201
    except Exception as e:
        return jsonify(
            message=f"Failed to update folder progress: {e}",
            status=500
        ), 500
# --------------END CHANGE------------

@folder_bp.route('/folder/delete/<folder_id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
@has_folder_rights
def deletefolder(folder_id):
    '''This method is called when the user requests to delete a folder.'''
    try:
        db.child("folder").child(folder_id).remove()

        return jsonify(
            message='Folder deleted successfully',
            status=200
        ), 200
    except Exception as e:
        return jsonify(
            message=f"Failed to delete folder: {e}",
            status=500
        ), 500


@folder_bp.route('/deck/add-deck', methods=['POST'])
@cross_origin(supports_credentials=True)
@has_folder_and_deck_rights
def adddecktofolder():
    '''This method allows the user to add a deck to a folder by folderId and deckId.'''
    try:
        data = request.get_json()
        folder_id = data['folderId']
        deck_id = data['deckId']

        db.child("folder_deck").push({
            "folderId": folder_id,
            "deckId": deck_id
        })

        return jsonify(
            message='Deck added to folder successfully',
            status=201
        ), 201
    except Exception as e:
        return jsonify(
            message=f"Failed to add deck to folder: {e}",
            status=500
        ), 500
    
@folder_bp.route('/deck/get-deck/<folder_id>', methods=['GET'])
@cross_origin(supports_credentials=True)
@has_folder_rights
def get_deck_from_folder(folder_id):
    '''Return decks in a folder'''
    try:
        deck_list = []
        folder_deck_ref = db.child("folder_deck").order_by_child("folderId").equal_to(folder_id).get()
        for fd in folder_deck_ref.each():
            if fd.val().get('deckId') is None:
                continue
            deck_list.append(fd.val().get('deckId'))
        print(deck_list)

        return jsonify(
            decks=deck_list,
            message='Deck returned',
            status=201
        ), 201
    except Exception as e:
        return jsonify(
            message=f"Failed to returned deck: {e}",
            status=500
        ), 500


@folder_bp.route('/folder/remove-deck', methods=['DELETE'])
@cross_origin(supports_credentials=True)
@has_folder_and_deck_rights
def removedeckfromfolder():
    '''This method allows the user to remove a deck from a folder by folderId and deckId.'''
    try:
        data = request.get_json()
        folder_id = data['folderId']
        deck_id = data['deckId']

        folder_deck_ref = db.child("folder_deck").order_by_child("folderId").equal_to(folder_id).get()
        for fd in folder_deck_ref.each():
            if fd.val().get('deckId') == deck_id:
                db.child("folder_deck").child(fd.key()).remove()
                break

        return jsonify(
            message='Deck removed from folder successfully',
            status=200
        ), 200
    except Exception as e:
        return jsonify(
            message=f"Failed to remove deck from folder: {e}",
            status=500
        ), 500
    
@folder_bp.route('/decks/<folder_id>', methods=['GET'])
@cross_origin(supports_credentials=True)
@has_folder_rights
def get_decks_for_folder(folder_id):
    '''This method is called to fetch all decks for a specific folder.'''
    try:
        folder_obj = db.child("folder_deck").order_by_child("folderId").equal_to(folder_id).get()
        deck_list = []
        for folders in folder_obj.each():
            obj = folders.val()
            print("obj: ", obj)
            obj['id'] = folders.key()  # Optional: if you need the deck ID
            print(obj['id'])
            deck_list.append(obj["id"])
        print("deck_list", deck_list)
        deck_title = []
        for deck in deck_list:
            deck_obj = db.child("deck").child(deck).get()
            print(deck_obj)
            print(deck_obj.key())
            title = deck_obj.val()["title"]
            print(title)
            deck_title.append( {"id": deck, "title": title} )

        return jsonify(
            decks=deck_title,
            message='Fetched decks successfully',
            status=200
        ), 200
    except Exception as e:
        print(e)
        return jsonify(
            decks=[],
            message=f"An error occurred: {e}",
            status=500
        ), 500