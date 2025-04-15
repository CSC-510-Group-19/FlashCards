import json
import unittest
from unittest.mock import patch, Mock, MagicMock
from flask import Flask, jsonify
from oauth2client.contrib.xsrfutil import validate_token
from src.folders.routes import folder_bp  # Adjust the import based on your app structure
import sys
from pathlib import Path
from __init__ import *

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

class TestFolders(unittest.TestCase):
    good_auth_header = {'Authorization': '-auth123'}
    bad_auth_header = {'Authorization': '-auth1234'}
    good_auth_response = {"users": [{"localId": "-123"}]}
    bad_auth_response = {"message": "Invalid token"}
    mockGoodAuth = Mock(return_value=good_auth_response)
    mockBadAuth = Mock(return_value=bad_auth_response)
    mockNoAuth = Mock(return_value={})

    mockUserOwnsFolder = Mock(return_value=True)
    mockUnauthorized = {"message": "Unauthorized"}, 401
    mockFolderNotFound = {"message": "Folder not found"}, 404
    mockUnexpectedResponse = {"message": "Unexpected error"}, 500

    @classmethod
    def setUp(cls):
        cls.app = Flask(__name__, instance_relative_config=False)
        cls.app.register_blueprint(folder_bp)
        cls.app = cls.app.test_client()


    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_get_folders_success(self, mock_db):
        '''Test successful fetch of all folders for a user'''
        user_id = "test_user_id"
        
        # Mock folder data
        mock_folders_data = [
            MagicMock(key=lambda: 'folder_id_1', val=lambda: {"name": "Folder 1", "userId": user_id}),
            MagicMock(key=lambda: 'folder_id_2', val=lambda: {"name": "Folder 2", "userId": user_id}),
        ]
        
        # Configure mock database response for folders
        mock_db.child.return_value.order_by_child.return_value.equal_to.return_value.get.return_value.each.return_value = mock_folders_data

        response = self.app.get(f'/folders/all?userId={user_id}', headers= self.auth_header)
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        # Assert the response data is as expected
        assert len(response_data['folders']) == 2
        assert response_data['folders'][0]['name'] == "Folder 1"
        assert response_data['folders'][1]['name'] == "Folder 2"


    @patch('src.__init__.get_user_id_from_request', return_value=mockNoAuth)
    async def test_get_folders_no_user_id(self):
        '''Test fetch all folders without userId returns error'''
        response = self.app.get(f'/folders/all')
        assert response.status_code == 500

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_create_folder_success(self, mock_db):
        '''Test successful folder creation'''
        mock_db.child.return_value.push.return_value = {"name": "folder_id"}  # Simulate a folder reference
        folder_data = {"name": "My New Folder", "userId": "test_user_id"}

        response = self.app.post('/folder/create', data=json.dumps(folder_data), content_type='application/json')
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['folder']['name'] == "My New Folder"
        assert response_data['message'] == 'Folder created successfully'

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_create_folder_error(self, mock_db):
        '''Test folder creation failure due to missing data'''
        folder_data = {"userId": "test_user_id"}  # Missing name
        response = self.app.post('/folder/create', data=json.dumps(folder_data), content_type='application/json')
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert "Failed to create folder" in response_data['message']

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockBadAuth)
    async def test_create_folder_invalid_auth(self, mock_db):
        '''Test folder creation failure due to invalid auth'''
        folder_data = {"userId": "test_user_id"}
        response = self.app.post('/folder/create', data=json.dumps(folder_data), content_type='application/json')
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert "Invalid token" in response_data['message']


    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_folder', return_value=mockUserOwnsFolder)
    async def test_update_folder_success(self, mock_db):
        '''Test successful folder update'''
        folder_id = "folder_id"
        mock_db.child.return_value.child.return_value.update.return_value = None  # Simulate successful update
        folder_data = {"name": "Updated Folder Name"}

        response = self.app.patch(f'/folder/update/{folder_id}', data=json.dumps(folder_data), content_type='application/json')
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Folder updated successfully'

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_folder')
    async def test_update_folder_error(self, mock_db):
        '''Test folder update failure'''
        folder_id = "folder_id"
        folder_data = {"name": "Updated Folder Name"}

        mock_db.child.return_value.child.return_value.update.side_effect = Exception("Update failed")
        
        response = self.app.patch(f'/folder/update/{folder_id}', data=json.dumps(folder_data), content_type='application/json')
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert "Unexpected error" in response_data['message']

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_update_folder_not_found(self, mock_db):
        '''Test update failure when folder not found'''
        folder_id = "folder_id"
        folder_data = {"name": "Updated Folder Name"}
        mock_db.child.return_value.child.return_value.update.side_effect = Exception("Folder not found")

        response = self.app.patch(f'/folder/update/{folder_id}', data=json.dumps(folder_data), content_type='application/json')
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert "Folder not found" in response_data['message']

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_folder', return_value=mockUserOwnsFolder)
    async def test_unauthorized_folder_update(self, mock_db):
        '''Test unauthorized folder update'''
        folder_id = "folder_id"
        folder_data = {"name": "Updated Folder Name"}

        response = self.app.patch(f'/folder/update/{folder_id}', data=json.dumps(folder_data), content_type='application/json')

        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert "Unauthorized" in response_data['message']


    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_folder', return_value=mockUserOwnsFolder)
    async def test_delete_folder_success(self, mock_db):
        '''Test successful folder deletion'''
        folder_id = "folder_id"
        mock_db.child.return_value.child.return_value.remove.return_value = None  # Simulate successful removal

        response = self.app.delete(f'/folder/delete/{folder_id}')
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Folder deleted successfully'

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_delete_folder_error(self, mock_db):
        '''Test folder deletion failure'''
        folder_id = "folder_id"
        mock_db.child.return_value.child.return_value.remove.side_effect = Exception("Delete failed")

        response = self.app.delete(f'/folder/delete/{folder_id}')
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert "Unexpected error" in response_data['message']

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_delete_folder_not_found(self, mock_db):
        '''Test update failure when folder not found'''
        folder_id = "folder_id"
        mock_db.child.return_value.child.return_value.update.side_effect = Exception("Folder not found")

        response = self.app.delete(f'/folder/delete/{folder_id}')
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert "Folder not found" in response_data['message']

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_add_deck_to_folder_success(self, mock_db):
        '''Test successful addition of a deck to a folder'''
        deck_data = {"folderId": "folder_id", "deckId": "deck_id"}
        response = self.app.post('/deck/add-deck', data=json.dumps(deck_data), content_type='application/json')
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Deck added to folder successfully'

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_folder', return_value=mockUnauthorized)
    async def test_add_deck_to_folder_error(self, mock_db):
        '''Test unauthorized addition of a deck to a folder'''
        deck_data = {"folderId": "folder_id", "deckId": "deck_id"}
        response = self.app.post('/deck/add-deck', data=json.dumps(deck_data), content_type='application/json')
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert "Unauthorized" in response_data['message']

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_add_deck_to_folder_error(self, mock_db):
        '''Test failure when adding a deck to a folder'''
        deck_data = {"folderId": "folder_id", "deckId": "deck_id"}
        mock_db.child.return_value.push.side_effect = Exception("Add failed")

        response = self.app.post('/deck/add-deck', data=json.dumps(deck_data), content_type='application/json')
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert "Unexpected error" in response_data['message']

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_folder', return_value=mockUserOwnsFolder)
    async def test_remove_deck_from_folder_success(self, mock_db):
        '''Test successful removal of a deck from a folder'''
        deck_data = {"folderId": "folder_id", "deckId": "deck_id"}
        response = self.app.delete('/folder/remove-deck', data=json.dumps(deck_data), content_type='application/json')
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Deck removed from folder successfully'

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_remove_deck_from_folder_error(self, mock_db):
        '''Test failure when removing a deck from a folder'''
        deck_data = {"folderId": "folder_id", "deckId": "deck_id"}
        mock_db.child.return_value.order_by_child.return_value.equal_to.return_value.get.side_effect = Exception("Remove failed")

        response = self.app.delete('/folder/remove-deck', data=json.dumps(deck_data), content_type='application/json')
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert "Failed to remove deck from folder" in response_data['message']

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_folder', return_value=mockUnauthorized)
    async def test_remove_deck_from_folder_error(self, mock_db):
        '''Test unauthorized removal of a deck from a folder'''
        deck_data = {"folderId": "folder_id", "deckId": "deck_id"}

        response = self.app.delete('/folder/remove-deck', data=json.dumps(deck_data), content_type='application/json')
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert "Unauthorized" in response_data['message']

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_remove_deck_from_folder_folder_not_found(self, mock_db):
        '''Test unauthorized removal of a deck from a non-existent folder'''
        deck_data = {"folderId": "folder_id", "deckId": "deck_id"}
        mock_db.child.return_value.order_by_child.return_value.equal_to.return_value.get.side_effect = None

        response = self.app.delete('/folder/remove-deck', data=json.dumps(deck_data), content_type='application/json')
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert "Folder not found" in response_data['message']

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_folder', return_value=mockUserOwnsFolder)
    async def test_remove_deck_from_folder_deck_not_found(self, mock_db):
        '''Test unauthorized removal of a deck from a non-existent deck'''
        deck_data = {"folderId": "folder_id", "deckId": "deck_id"}
        mock_db.child.return_value.order_by_child.return_value.equal_to.return_value.get.side_effect = None

        response = self.app.delete('/folder/remove-deck', data=json.dumps(deck_data), content_type='application/json')
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert "Folder not found" in response_data['message']

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_folder', return_value=mockUserOwnsFolder)
    async def test_get_decks_for_folder_success(self, mock_db):
        '''Test successful retrieval of decks for a folder'''
        folder_id = "folder_id"

        # Mock the folder_deck response for folder decks query
        mock_folder_deck_data = [
            MagicMock(key=lambda: 'deck_id_1', val=lambda: {"deckId": "deck_id_1"}),
            MagicMock(key=lambda: 'deck_id_2', val=lambda: {"deckId": "deck_id_2"}),
        ]
        mock_db.child.return_value.order_by_child.return_value.equal_to.return_value.get.return_value.each.return_value = mock_folder_deck_data

        # Mock the individual deck data for each deck in the deck list
        mock_deck_1 = MagicMock(val=lambda: {"title": "Deck 1"})
        mock_deck_2 = MagicMock(val=lambda: {"title": "Deck 2"})
        mock_db.child.return_value.child.return_value.get.side_effect = [mock_deck_1, mock_deck_2]

        # Make the API call
        response = self.app.get(f'/decks/{folder_id}')

        # Assert response status and data
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data['decks']) == 2
        assert response_data['decks'][0]['title'] == "Deck 1"
        assert response_data['decks'][1]['title'] == "Deck 2"

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_folder', return_value=mockUserOwnsFolder)
    async def test_get_decks_for_folder_error(self, mock_db):
        '''Test failure when retrieving decks for a folder'''
        folder_id = "folder_id"
        mock_db.child.return_value.order_by_child.return_value.equal_to.return_value.get.side_effect = Exception("Retrieval failed")

        response = self.app.get(f'/decks/{folder_id}')
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert "An error occurred: Retrieval failed" in response_data['message']

    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_folder', return_value=mockUserOwnsFolder)
    async def test_get_decks_for_folder_no_decks(self, mock_db):
        '''Test retrieval of decks for a folder with no decks'''
        folder_id = "folder_id"
        
        # Mock the folder_deck response for folder decks query
        mock_db.child.return_value.order_by_child.return_value.equal_to.return_value.get.return_value.each.return_value = []

        response = self.app.get(f'/decks/{folder_id}')
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data['decks']) == 0
    
    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_folder', return_value=mockUserOwnsFolder)
    async def test_get_decks_for_folder_no_folder(self, mock_db):
        '''Test retrieval of decks for a non-existent folder'''
        folder_id = "non_existent_folder"
        
        # Mock the folder_deck response for folder decks query
        mock_db.child.return_value.order_by_child.return_value.equal_to.return_value.get.return_value.each.return_value = []

        response = self.app.get(f'/decks/{folder_id}')
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data == self.mockUnexpectedResponse
    
    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_folder', return_value=mockUserOwnsFolder)
    async def test_get_decks_for_folder_invalid_folder_id(self, mock_db):
        '''Test retrieval of decks for an invalid folder ID'''
        folder_id = "invalid_folder_id"
        
        # Mock the folder_deck response for folder decks query
        mock_db.child.return_value.order_by_child.return_value.equal_to.return_value.get.return_value.each.return_value = []

        response = self.app.get(f'/decks/{folder_id}')
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data['decks']) == 0
    
    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockBadAuth)
    @patch('src.__init__.user_owns_folder', return_value=mockUserOwnsFolder)
    async def test_get_decks_for_folder_no_user_id(self, mock_db):
        '''Test retrieval of decks for a folder without userId'''
        response = self.app.get(f'/decks/')
        assert response.status_code == 500

    @patch('src.folders.routes.db')
    async def test_deck_progress_uninitialized(self, mock_db):
        '''Test deck progress when it is uninitialized'''
        folder_id = "folder_id"
        deck_id = "deck_id"
        
        # Mock the folder_deck response for folder decks query
        mock_db.child.return_value.order_by_child.return_value.equal_to.return_value.get.return_value.each.return_value = []

        response = self.app.get(f'/decks/{folder_id}/{deck_id}')
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['progress'] == 0

    @patch('src.folders.routes.db')
    async def test_folder_progress_uninitialized(self, mock_db):
        '''Test folder progress when it is uninitialized'''
        folder_id = "folder_id"
        
        # Mock the folder_deck response for folder decks query
        mock_db.child.return_value.order_by_child.return_value.equal_to.return_value.get.return_value.each.return_value = []

        response = self.app.get(f'/folders/{folder_id}')
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['progress'] == 0
    
    @patch('src.folders.routes.db')
    async def test_folder_progress_success(self, mock_db):
        '''Test folder progress when it is successfully initialized'''
        folder_id = "folder_id"
        
        # Mock the folder_deck response for folder decks query
        mock_db.child.return_value.order_by_child.return_value.equal_to.return_value.get.return_value.each.return_value = []

        # Mock the deck progress response
        mock_db.child.return_value.child.return_value.get.return_value.val.return_value = {"progress": 50}

        response = self.app.get(f'/folders/{folder_id}')
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['progress'] == 50
    
    @patch('src.folders.routes.db')
    async def test_deck_progress_success(self, mock_db):
        '''Test deck progress when it is successfully initialized'''
        folder_id = "folder_id"
        deck_id = "deck_id"
        
        # Mock the folder_deck response for folder decks query
        mock_db.child.return_value.order_by_child.return_value.equal_to.return_value.get.return_value.each.return_value = []

        # Mock the deck progress response
        mock_db.child.return_value.child.return_value.get.return_value.val.return_value = {"progress": 50}

        response = self.app.get(f'/decks/{folder_id}/{deck_id}')
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['progress'] == 50
    
    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_folder', return_value=mockUserOwnsFolder)
    async def test_get_decks_in_folder_equals_num_decks(self, mock_db):
        '''Test when the number of decks shown in a folder accurately reflects the number of decks in the folder'''
        folder_id = "folder_id"
        
        # Mock the folder_deck response for folder decks query
        mock_db.child.return_value.order_by_child.return_value.equal_to.return_value.get.return_value.each.return_value = []

        # Mock the deck list response
        mock_db.child.return_value.child.return_value.get.return_value.val.return_value = {"decks": ['deck A ', 'deck B']}

        # Make the API call
        response = self.app.get(f'/decks/{folder_id}')
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['decks'] == ['deck A ', 'deck B']
    
    @patch('src.folders.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_folder', return_value=mockUserOwnsFolder)
    async def test_get_decks_in_folder_fail(self, mock_db):
        '''Test when the number of decks shown in a folder does not accurately reflect the number of decks in the folder'''
        folder_id = "folder_id"
        
        # Mock the folder_deck response for folder decks query
        mock_db.child.return_value.order_by_child.return_value.equal_to.return_value.get.return_value.each.return_value = []

        # Mock the deck list response
        mock_db.child.return_value.child.return_value.get.return_value.val.return_value = {"decks": ['deck A ', 'deck B']}

        # Make the API call
        response = self.app.get(f'/decks/{folder_id}')
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data['decks'] != ['deck A ', 'deck B']