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
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from __init__ import firebase


folder_bp = Blueprint(
    'folder_bp', __name__
)

db = firebase.database()

@folder_bp.route('/folder/<id>', methods=['GET'])
@cross_origin(supports_credentials=True)
def getfolder(id):
    '''This method is called when we want to fetch one of the folders by folder ID'''
    try:
        folder = db.child("folder").child(id).get()
        return jsonify(
            folder=folder.val(),
            message='Fetched folder successfully',
            status=200
        ), 200
    except Exception as e:
        return jsonify(
            folder={},
            message=f"An error occurred: {e}",
            status=400
        ), 400


@folder_bp.route('/folders/all', methods=['GET'])
@cross_origin(supports_credentials=True)
def getfolders():
    '''This method is called when we want to fetch all folders for a specific user'''
    args = request.args
    userId = args and args['userId']
    try:
        user_folders = db.child("folder").order_by_child("userId").equal_to(userId).get()
        folders = []
        for folder in user_folders.each():
            obj = folder.val()
            obj['id'] = folder.key()
            decks = db.child("folder_deck").order_by_child("folderId").equal_to(folder.key()).get()
            obj['decks_count'] = len(decks.val()) if decks.val() else 0
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
            status=400
        ), 400


@folder_bp.route('/folder/create', methods=['POST'])
@cross_origin(supports_credentials=True)
def createfolder():
    '''This method is called when the user requests to create a new folder.'''
    try:
        data = request.get_json()
        folder_name = data['name']
        user_id = data['userId']

        db.child("folder").push({
            "name": folder_name,
            "userId": user_id
        })

        return jsonify(
            message='Folder created successfully',
            status=201
        ), 201
    except Exception as e:
        return jsonify(
            message=f"Failed to create folder: {e}",
            status=400
        ), 400


@folder_bp.route('/folder/update/<id>', methods=['PATCH'])
@cross_origin(supports_credentials=True)
def updatefolder(id):
    '''This method is called when the user wants to update a folder's name.'''
    try:
        data = request.get_json()
        folder_name = data.get('name')

        db.child("folder").child(id).update({
            "name": folder_name
        })

        return jsonify(
            message='Folder updated successfully',
            status=201
        ), 201
    except Exception as e:
        return jsonify(
            message=f"Failed to update folder: {e}",
            status=400
        ), 400


@folder_bp.route('/folder/delete/<id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def deletefolder(id):
    '''This method is called when the user requests to delete a folder.'''
    try:
        db.child("folder").child(id).remove()

        return jsonify(
            message='Folder deleted successfully',
            status=200
        ), 200
    except Exception as e:
        return jsonify(
            message=f"Failed to delete folder: {e}",
            status=400
        ), 400


@folder_bp.route('/folder/add-deck', methods=['POST'])
@cross_origin(supports_credentials=True)
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
            status=400
        ), 400


@folder_bp.route('/folder/remove-deck', methods=['DELETE'])
@cross_origin(supports_credentials=True)
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
            status=400
        ), 400
