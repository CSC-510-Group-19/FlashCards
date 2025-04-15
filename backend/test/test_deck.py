from flask import Flask
import sys
sys.path.append('backend/src')
import unittest
from unittest.mock import patch, MagicMock, ANY, Mock
import json
from src.auth.routes import auth_bp
from src.deck.routes import deck_bp
from src.cards.routes import card_bp
from datetime import datetime
import pytest
from pathlib import Path
from unittest.mock import call

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))


class TestDeck(unittest.TestCase):
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
    def setUp(self):
        self.app=Flask(__name__, instance_relative_config=False)
        self.app.register_blueprint(deck_bp)
        self.app=self.app.test_client()
        # self.client = self.app.test_client()

    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_deck_id_route_get_valid_id(self):
        '''Test the deck/id route of our app with a valid deck id'''
        with self.app:
            self.app.post('/login', data=json.dumps(dict(email='aaronadb@gmail.com', password='flashcards123')), content_type='application/json', follow_redirects=True)
            self.app.post('/deck/create', data=json.dumps(dict(localId='Test', title='TestDeck', description='This is a test deck', visibility='public')), content_type='application/json')
            response = self.app.get('/deck/Test')
            assert response.status_code == 200

    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_deck_id_route_post(self):
        '''Test the deck/id route of our app with the post method'''
        with self.app:
            self.app.post('/login', data=json.dumps(dict(email='aaronadb@gmail.com', password='flashcards123')), content_type='application/json', follow_redirects=True)
            self.app.post('/deck/create', data=json.dumps(dict(localId='Test', title='TestDeck', description='This is a test deck', visibility='public')), content_type='application/json')
            response = self.app.post('/deck/Test')
            assert response.status_code == 405

    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_deck_all_route(self):
        '''Test the deck/all route of our app'''
        response=self.app.get('/deck/all',query_string=dict(localId='Test'))
        assert response.status_code==200

    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_deck_all_route_post(self):
        '''Test that the post request to the '/deck/all' route is not allowed'''
        response=self.app.post('/deck/all')
        assert response.status_code==405

    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_create_deck_route(self):
        '''Test the create deck route of our app'''
        response = self.app.post('/deck/create', data=json.dumps(dict(localId='Test', title='TestDeck', description='This is a test deck', visibility='public')), content_type='application/json')
        assert response.status_code == 201

    @patch('src.__init__.get_user_id_from_request', return_value=mockBadAuth)
    async def test_create_deck_with_invalid_token(self):
        '''Test the create deck route of our app with an invalid token'''
        response = self.app.post('/deck/create', data=json.dumps(dict(localId='Test', title='TestDeck', description='This is a test deck', visibility='public')), content_type='application/json')
        assert response.status_code == 403

    @patch('src.__init__.get_user_id_from_request', return_value=mockNoAuth)
    async def test_create_deck_with_no_token(self):
        '''Test the create deck route of our app with an invalid token'''
        response = self.app.post('/deck/create', data=json.dumps(dict(localId='Test', title='TestDeck', description='This is a test deck', visibility='public')), content_type='application/json')
        assert response.status_code == 401

    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_update_deck_route_post(self):
        '''Test the deck/update route of our app with'''
        with self.app:
            self.app.post('/login', data=json.dumps(dict(email='aaronadb@gmail.com', password='flashcards123')), content_type='application/json', follow_redirects=True)
            self.app.post('/deck/create', data=json.dumps(dict(localId='Test', title='TestDeck', description='This is a test deck', visibility='public')), content_type='application/json')
            response = self.app.patch('/deck/update/Test', data=json.dumps(dict(localId='Test', title='TestDeck', description='This is a test deck', visibility='public')), content_type='application/json')
            assert response.status_code == 201

    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_delete_deck_route_post(self):
        '''Test the deck/delete route of our app with'''
        with self.app:
            self.app.post('/login', data=json.dumps(dict(email='aaronadb@gmail.com', password='flashcards123')), content_type='application/json', follow_redirects=True)
            self.app.post('/deck/create', data=json.dumps(dict(localId='Test', title='TestDeck', description='This is a test deck', visibility='public')), content_type='application/json')
            response = self.app.delete('/deck/delete/Test')
            assert response.status_code == 200

    @patch('src.__init__.get_user_id_from_request', return_value=mockBadAuth)
    async def test_delete_deck_with_invalid_token(self):
        '''Test the deck/delete route of our app with an invalid token'''
        response = self.app.delete('/deck/delete/Test')
        assert response.status_code == 403

    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_deck', return_value=mockUnauthorized)
    async def test_delete_deck_unauthorized(self):
        '''Test the deck/delete when unauthorized'''
        response = self.app.delete('/deck/delete/Test')
        assert response.status_code == 401

    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_update_last_opened_deck_route_failure(self):
        '''Test the deck/updateLastOpened/<id> route of our app with failure scenario'''
        with self.app:
            # Arrange: Mock the database update to raise an exception
            with patch('src.deck.routes.db.child') as mock_db:
                mock_db.return_value.child.return_value.update.side_effect = Exception("Database update failed")

                # Simulate user login and deck creation
                self.app.post('/login', data=json.dumps(dict(email='aaronadb@gmail.com', password='flashcards123')), content_type='application/json', follow_redirects=True)
                self.app.post('/deck/create', data=json.dumps(dict(localId='Test', title='TestDeck', description='This is a test deck', visibility='public')), content_type='application/json')

                # Act: Send a request to update the last opened timestamp
                response = self.app.patch('/deck/updateLastOpened/Test', content_type='application/json')

                # Assert: Check the response status code for failure
                assert response.status_code == 500
                response_data = json.loads(response.data)
                assert response_data['message'] == 'Failed to update lastOpened: Database update failed'
    
    @patch('src.deck.routes.db')  # Mock the database connection
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_get_leaderboard_route(self, mock_db):
        '''Test the deck/<deckId>/leaderboard route of our app'''
        with self.app:
            # Arrange: Set up mock return value for leaderboard entries
            mock_entries = MagicMock()
            mock_entries.each.return_value = [
                MagicMock(val=lambda: {"userEmail": "user1@example.com", "correct": 10, "incorrect": 2, "lastAttempt": "2024-01-01T12:00:00"}),
                MagicMock(val=lambda: {"userEmail": "user2@example.com", "correct": 15, "incorrect": 1, "lastAttempt": " 2024-01-02T12:00:00"}),
                MagicMock(val=lambda: {"userEmail": "user3@example.com", "correct": 5, "incorrect": 0, "lastAttempt": "2024-01-03T12:00:00"}),
            ]
            mock_db.child.return_value.child.return_value.get.return_value = mock_entries

            # Act: Send a request to get the leaderboard for a specific deck
            response = self.app.get('/deck/TestDeck/leaderboard')

            # Assert: Check the response status code and the content of the response
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['status'] == 200
            assert len(response_data['leaderboard']) == 3
            assert response_data['leaderboard'][0]['userEmail'] == "user2@example.com"  # Highest score
            assert response_data['leaderboard'][1]['userEmail'] == "user1@example.com"  # Second highest score
            assert response_data['leaderboard'][2]['userEmail'] == "user3@example.com"  # Lowest score
          
    @patch('src.deck.routes.db')  # Mock the database connection
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_update_leaderboard_success(self, mock_db):
        '''Test the /deck/<deck_id>/update-leaderboard route of our app for a successful update'''
        with self.app:
            # Arrange: Set up mock data
            deck_id = "TestDeck"
            user_id = "user123"
            user_email = "user@example.com"
            correct = 10
            incorrect = 2

            # Mock the database update
            mock_leaderboard_ref = MagicMock()
            mock_db.child.return_value.child.return_value.child.return_value = mock_leaderboard_ref

            # Act: Send a POST request to update the leaderboard
            response = self.app.post(f'/deck/{deck_id}/update-leaderboard', 
                                    data=json.dumps({
                                        "userId": user_id,
                                        "userEmail": user_email,
                                        "correct": correct,
                                        "incorrect": incorrect
                                    }), 
                                    content_type='application/json')

            # Assert: Check the response status code and message
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['message'] == "Leaderboard updated successfully"

            # Assert that the database update was called with the correct parameters
            mock_leaderboard_ref.update.assert_called_once_with({
                "userEmail": user_email,
                "correct": correct,
                "incorrect": incorrect,
                "lastAttempt": ANY  # Check that it's called but not the exact timestamp
            })

    @patch('src.deck.routes.db')  # Mock the database connection
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_get_user_score_success(self, mock_db):
        '''Test the /deck/<deckId>/user-score/<userId> route for a successful score fetch'''
        deck_id = "TestDeck"
        user_id = "user123"

        # Mock the database return value for a user that exists
        mock_leaderboard_entry = MagicMock()
        mock_leaderboard_entry.val.return_value = {
            "correct": 10,
            "incorrect": 2
        }
        mock_db.child.return_value.child.return_value.child.return_value.get.return_value = mock_leaderboard_entry

        # Act: Send a GET request to fetch the user's score
        response = self.app.get(f'/deck/{deck_id}/user-score/{user_id}')

        # Assert: Check the response status code and message
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['score'] == {
            "correct": 10,
            "incorrect": 2
        }
        assert response_data['message'] == "User score fetched successfully"

    @patch('src.deck.routes.db')  # Mock the database connection
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_get_user_score_no_entry(self, mock_db):
        '''Test the /deck/<deckId>/user-score/<userId> route when no score entry exists'''
        deck_id = "TestDeck"
        user_id = "user123"

        # Mock the database return value for a user that does not exist
        mock_leaderboard_entry = MagicMock()
        mock_leaderboard_entry.val.return_value = None
        mock_db.child.return_value.child.return_value.child.return_value.get.return_value = mock_leaderboard_entry

        # Act: Send a GET request to fetch the user's score
        response = self.app.get(f'/deck/{deck_id}/user-score/{user_id}')

        # Assert: Check the response status code and message
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['score'] == {
            "correct": 0,
            "incorrect": 0
        }
        assert response_data['message'] == "No score found for the user, returning zeros."

    @patch('src.deck.routes.db')  # Mock the database connection
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_get_user_score_error(self, mock_db):
        '''Test the /deck/<deckId>/user-score/<userId> route when an error occurs'''
        deck_id = "TestDeck"
        user_id = "user123"

        # Simulate an exception when accessing the database
        mock_db.child.return_value.child.return_value.child.return_value.get.side_effect = Exception("Database error")

        # Act: Send a GET request to fetch the user's score
        response = self.app.get(f'/deck/{deck_id}/user-score/{user_id}')

        # Assert: Check the response status code and message
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data['message'] == "An error occurred: Database error"

    @patch('src.deck.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_get_deck_error(self, mock_db):
        '''Test error handling in getdeck route'''
        # Mock the database to raise an exception
        mock_db.child.return_value.child.return_value.get.side_effect = Exception("Database error")
        
        response = self.app.get('/deck/Test')
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data['decks'] == []
        assert "An error occurred: Database error" in response_data['message']

    @patch('src.deck.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_get_decks_with_cards(self, mock_db):
        '''Test getdecks route with cards count'''
        # Create mock objects
        mock_deck = MagicMock()
        mock_deck_data = {
            "userId": "Test",
            "title": "TestDeck",
            "description": "Test Description",
            "visibility": "public"
        }
        mock_deck.val.return_value = mock_deck_data
        mock_deck.key.return_value = "deck123"

        # Create mock for decks query
        mock_decks_query = MagicMock()
        mock_decks_query.each.return_value = [mock_deck]

        # Create mock for cards query
        mock_cards_query = MagicMock()
        mock_cards_query.val.return_value = {"card1": {}, "card2": {}}  # Two cards

        # Set up the chain for deck query
        mock_db.child.return_value.order_by_child.return_value.equal_to.return_value.get.side_effect = [
            mock_decks_query,  # First call for decks
            mock_cards_query   # Second call for cards
        ]

        # Make the request
        response = self.app.get('/deck/all', query_string=dict(localId='Test'))
        
        # Assertions
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data['decks']) > 0  # Verify we have at least one deck
        assert response_data['decks'][0]['cards_count'] == 2
        assert response_data['decks'][0]['title'] == 'TestDeck'
        assert response_data['decks'][0]['id'] == 'deck123'

        # Verify the mock calls
        mock_db.child.assert_has_calls([
            call("deck"),
            call("card")
        ], any_order=True)

    @patch('src.deck.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_get_decks_error(self, mock_db):
        '''Test error handling in getdecks route'''
        # Mock the database to raise an exception
        mock_db.child.return_value.order_by_child.return_value.equal_to.side_effect = Exception("Database error")

        response = self.app.get('/deck/all', query_string=dict(localId='Test'))
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data['decks'] == []
        assert "An error occurred Database error" in response_data['message']

    @patch('src.deck.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_deck', return_value=True)
    async def test_update_deck_error(self, mock_db):
        '''Test error handling in update route'''
        # Mock the database to raise an exception
        mock_db.child.return_value.child.return_value.update.side_effect = Exception("Database error")

        response = self.app.patch('/deck/update/Test', 
                                data=json.dumps(dict(
                                    localId='Test',
                                    title='TestDeck',
                                    description='Test Description',
                                    visibility='public'
                                )),
                                content_type='application/json')
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert "Update Deck Failed Database error" in response_data['message']

    @patch('src.deck.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_deck', return_value=True)
    async def test_delete_deck_error(self, mock_db):
        '''Test error handling in delete route'''
        # Mock the database to raise an exception
        mock_db.child.return_value.child.return_value.remove.side_effect = Exception("Database error")

        response = self.app.delete('/deck/delete/Test')
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert "Delete Deck Failed Database error" in response_data['message']

    @patch('src.deck.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_get_leaderboard_error(self, mock_db):
        '''Test error handling in get_leaderboard route'''
        # Mock the database to raise an exception
        mock_db.child.return_value.child.return_value.get.side_effect = Exception("Database error")

        response = self.app.get('/deck/TestDeck/leaderboard')
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data['leaderboard'] == []
        assert "An error occurred: Database error" in response_data['message']

    @patch('src.deck.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_update_leaderboard_missing_userid(self, mock_db):
        '''Test update_leaderboard route with missing userId'''
        response = self.app.post('/deck/TestDeck/update-leaderboard',
                               data=json.dumps({
                                   "userEmail": "test@example.com",
                                   "correct": 10,
                                   "incorrect": 2
                               }),
                               content_type='application/json')
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data['message'] == "User ID is required"

    @patch('src.deck.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_update_leaderboard_error(self, mock_db):
        '''Test error handling in update_leaderboard route'''
        # Mock the database to raise an exception
        mock_db.child.return_value.child.return_value.child.return_value.update.side_effect = Exception("Database error")

        response = self.app.post('/deck/TestDeck/update-leaderboard',
                               data=json.dumps({
                                   "userId": "test123",
                                   "userEmail": "test@example.com",
                                   "correct": 10,
                                   "incorrect": 2
                               }),
                               content_type='application/json')
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data['message'] == "Failed to update leaderboard"
        
    ## Streaks
        
    @patch('src.deck.routes.db.child')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_get_streak(self, mock_db_child):
        '''Test getting the streak for a deck'''
        mock_db_child.return_value.child.return_value.get.return_value.val.return_value = {"streak": 5}
        response = self.app.get('/deck/streak/Test')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['streak'], 5) 
        
    @patch('src.deck.routes.db.child')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_patch_streak(self, mock_db_child):
        '''Test updating the streak for a deck'''
        mock_db_child.return_value.child.return_value.get.return_value.val.return_value = {"streak": 5}
        mock_db_child.return_value.child.return_value.update.return_value = None
        
        response = self.app.patch('/deck/streak/Test', data=json.dumps({"streak": 6}), content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Streak updated')
        
    @patch("src.deck.routes.db.child")
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_get_streak_invalid_deck(self, mock_db_child):
        """Test retrieving streak for a non-existent deck."""
        mock_db_child.return_value.child.return_value.get.return_value.val.return_value = None
        response = self.app.get("/deck/streak/InvalidDeck")
        self.assertEqual(response.status_code, 404)
        
    
    @patch('src.deck.routes.db.child')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_patch_streak_invalid_deck(self, mock_db_child):
        """Test updating streak for a non-existent deck."""
        mock_db_child.return_value.child.return_value.get.return_value.val.return_value = None
        response = self.app.patch("/deck/streak/InvalidDeck", data=json.dumps({"streak": 7}), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        
    @patch("src.deck.routes.db.child")
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_patch_streak_invalid_data(self, mock_db_child):
        """Test updating the streak with invalid data."""
        invalid_payloads = [
            {"goal": "asdfghjkl"},                                              # random
            {"goal": 12345},                                                    # numbers
            {},                                                                 # no data
            {"goal": "Study this deck for 20 minutes", "extra_field": "oops"},  # extra field
            {"goal": "DROP TABLE users;"}                                       # SQL/code injection
        ]
        
        for payload in invalid_payloads:
            response = self.app.patch("/deck/streak/Test", data=json.dumps(payload), content_type="application/json")
            self.assertIn(response.status_code, [400, 422])  # Expecting a bad request or unprocessable entity
    
        
    ## Goals
        
    @patch('src.deck.routes.db.child')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_get_goal(self, mock_db_child):
        '''Test getting the goal for a deck'''
        study_goals = [
            "Study this deck for 20 minutes",
            "Take a quiz in this deck",
            "Add 5 new flashcards to this deck"
        ]
        mock_db_child.return_value.child.return_value.get.return_value.val.return_value = {
            "dailyGoal": "Study this deck for 20 minutes",
            "goalDate": "2024-02-25",
            "goalCompleted": False
        }
        response = self.app.get('/deck/goal/Test')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(data['goal'], study_goals)
        self.assertEqual(data['goalCompleted'], False)
        
    @patch('src.deck.routes.db.child')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_patch_goal(self, mock_db_child):
        '''Test updating the goal for a deck'''
        mock_db_child.return_value.child.return_value.get.return_value.val.return_value = {
            "goalProgress": 5,
        }
        response = self.app.patch("/deck/goal/Test", data=json.dumps({"goalCompleted": True}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        
    @patch("src.deck.routes.db.child")
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_get_goal_invalid_deck(self, mock_db_child):
        """Test retrieving goal for a non-existent deck."""
        mock_db_child.return_value.child.return_value.get.return_value.val.return_value = None
        response = self.app.get("/deck/goal/InvalidDeck")
        self.assertEqual(response.status_code, 404)
        
    @patch("src.deck.routes.db.child")
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_patch_goal_invalid_deck(self, mock_db_child):
        """Test updating goal for a non-existent deck."""
        mock_db_child.return_value.child.return_value.get.return_value.val.return_value = None
        response = self.app.patch("/deck/goal/InvalidDeck", data=json.dumps({"goalCompleted": True}), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        
    @patch("src.deck.routes.db.child")
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_patch_goal_invalid_data(self, mock_db_child):
        """Test updating the goal with invalid data."""
        invalid_payloads = [
            {"goal": "asdfghjkl"},                                              # random
            {"goal": 12345},                                                    # numbers
            {},                                                                 # no data
            {"goal": "Study this deck for 20 minutes", "extra_field": "oops"},  # extra field
            {"goal": "DROP TABLE users;"}                                       # SQL/code injection
        ]
        
        for payload in invalid_payloads:
            response = self.app.patch("/deck/goal/Test", data=json.dumps(payload), content_type="application/json")
            self.assertIn(response.status_code, [400, 422])  # Expecting a bad request or unprocessable entity
    
    @patch('src.deck.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_deck', return_value=True)
    async def test_deck_delete_route(self, mock_cards_db, mock_deck_db, mock_auth):
        '''Test the deck/delete/<id> route of our app'''
        responses = []
        response_1 = self.client.get('/deck/all?localId=Test')
        test_decks = response_1['decks']
        for test_deck in test_decks:
            test_deck_id = test_deck['id']
            response = self.client.post(
                '/deck/delete/' + test_deck_id,
                content_type='application/json'
            )
            responses.append(response)
        assert 500 not in responses

    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_create_deck_missing_fields(self):
        '''Test creating a deck with missing fields'''
        response = self.app.post(
            '/deck/create',
            data=json.dumps({
                'localId': 'Test',
                'title': '',
                'description': 'This is a test deck',
                'visibility': 'public'
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Missing required fields'

    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_deck', return_value=True)
    async def test_update_deck_invalid_data(self):
        '''Test updating a deck with invalid data'''
        response = self.app.patch(
            '/deck/update/Test',
            data=json.dumps({
                'localId': 'Test',
                'title': '',
                'description': 'This is a test deck',
                'visibility': 'public'
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Invalid data provided'

    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_deck', return_value=True)
    async def test_delete_deck_non_existent(self):
        '''Test deleting a non-existent deck'''
        response = self.app.delete('/deck/delete/non_existent_deck')
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Deck not found'

    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_deck', return_value=True)
    async def test_get_leaderboard_no_entries(self):
        '''Test fetching the leaderboard for a deck with no entries'''
        with patch('src.deck.routes.db.child') as mock_db:
            mock_db.return_value.child.return_value.get.return_value = None
            response = self.app.get('/deck/TestDeck/leaderboard')
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['leaderboard'] == []

    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_deck', return_value=True)
    async def test_update_leaderboard_missing_fields(self):
        '''Test updating the leaderboard with missing fields'''
        response = self.app.post(
            '/deck/TestDeck/update-leaderboard',
            data=json.dumps({
                'userId': 'Test',
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Missing required fields'
        
if __name__=="__main__":
    unittest.main()
