
from flask import Flask
import sys
sys.path.append('backend/src')
import unittest
import json
import pytest
from unittest.mock import patch, Mock
from src.auth.routes import auth_bp
from src.deck.routes import deck_bp
from src.cards.routes import card_bp
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

class CardTestApp(unittest.TestCase):
    good_auth_header = {'Authorization': '-auth123'}
    bad_auth_header = {'Authorization': '-auth1234'}
    good_auth_response = {"users": [{"localId": "-123"}]}
    bad_auth_response = {"message": "Invalid token"}
    mockGoodAuth = Mock(return_value=good_auth_response)
    mockBadAuth = Mock(return_value=bad_auth_response)
    mockNoAuth = Mock(return_value={})
    mockUnauthorized = Mock(return_value={"message": "Unauthorized"})

    @classmethod
    def setUpClass(cls):
        cls.app = Flask(__name__, instance_relative_config=False)
        cls.app.config['TESTING'] = True
        cls.app.register_blueprint(deck_bp)
        cls.app.register_blueprint(card_bp)
        cls.app.register_blueprint(auth_bp)
        cls.client = cls.app.test_client()

    def setUp(self):
        # Setup for each test method
        pass

    @patch('src.auth.routes.auth')
    @patch('src.deck.routes.db')
    @patch('src.cards.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_deck_card_all_route(self, mock_cards_db, mock_deck_db, mock_auth):
        '''Test the deck/card/all route of our app'''
        # Mock authentication
        mock_auth.sign_in_with_email_and_password.return_value = {
            'localId': 'Test',
            'idToken': 'some_token'
        }

        # Login
        self.client.post(
            '/login',
            data=json.dumps({
                'email': 'aaronadb@gmail.com',
                'password': 'flashcards123'
            }),
            content_type='application/json'
        )

        # Create deck
        self.client.get(
            '/deck/all',
            data=json.dumps({
                'localId': 'Test',
                'title': 'TestDeck',
                'description': 'This is a test deck',
                'visibility': 'public'
            }),
            content_type='application/json'
        )

        # Test get cards
        response = self.client.get('/deck/Test/card/all')
        self.assertEqual(response.status_code, 200)

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


    @patch('src.auth.routes.auth')
    @patch('src.deck.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_deck_card_all_route_post(self, mock_deck_db, mock_auth):
        '''Test that the post request to the '/deck/card/all' route is not allowed'''
        # Mock authentication
        mock_auth.sign_in_with_email_and_password.return_value = {
            'localId': 'Test',
            'idToken': 'some_token'
        }

        # Login
        self.client.post(
            '/login',
            data=json.dumps({
                'email': 'aaronadb@gmail.com',
                'password': 'flashcards123'
            }),
            content_type='application/json'
        )

        # Create deck
        self.client.post(
            '/deck/create',
            data=json.dumps({
                'localId': 'Test',
                'title': 'TestDeck',
                'description': 'This is a test deck',
                'visibility': 'public'
            }),
            content_type='application/json'
        )

        # Test post request to card/all
        response = self.client.post('/deck/Test/card/all')
        self.assertEqual(response.status_code, 405)

    @patch('src.auth.routes.auth')
    @patch('src.deck.routes.db')
    @patch('src.cards.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_deck_create_card_route(self, mock_cards_db, mock_deck_db, mock_auth):
        '''Test the create card in a deck route of our app'''
        # Mock authentication
        mock_auth.sign_in_with_email_and_password.return_value = {
            'localId': 'Test',
            'idToken': 'some_token'
        }

        # Mock database responses
        mock_cards_db.child.return_value.push.return_value = {'name': 'test_card_id'}

        # Login
        self.client.post(
            '/login',
            data=json.dumps({
                'email': 'aaronadb@gmail.com',
                'password': 'flashcards123'
            }),
            content_type='application/json'
        )

        # Create deck
        self.client.post(
            '/deck/create',
            data=json.dumps({
                'localId': 'Test',
                'title': 'TestDeck',
                'description': 'This is a test deck',
                'visibility': 'public'
            }),
            content_type='application/json'
        )

        # Create card
        response = self.client.post(
            '/deck/Test/card/create',
            data=json.dumps({
                'localId': 'Test',
                'cards': [{'front': 'front', 'back': 'back', 'hint': 'hint'}]
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
    

    @patch('src.auth.routes.auth')
    @patch('src.deck.routes.db')
    @patch('src.cards.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_get_cards_exception(self, mock_cards_db, mock_deck_db, mock_auth):
        '''Test the error handling of getcards method'''
        # Mock database to raise an exception
        mock_cards_db.child.return_value.order_by_child.return_value.equal_to.side_effect = Exception("Database error")

        response = self.client.get('/deck/Test/card/all')
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data['cards'], [])
        self.assertTrue('An error occurred' in data['message'])

    @patch('src.auth.routes.auth')
    @patch('src.deck.routes.db')
    @patch('src.cards.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_create_cards_exception(self, mock_cards_db, mock_deck_db, mock_auth):
        '''Test the error handling of createcards method'''
        # Mock database to raise an exception
        mock_cards_db.child.return_value.push.side_effect = Exception("Database error")

        response = self.client.post(
            '/deck/Test/card/create',
            data=json.dumps({
                'localId': 'Test',
                'cards': [{'front': 'front', 'back': 'back', 'hint': 'hint'}]
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Adding cards Failed')

    @patch('src.auth.routes.auth')
    @patch('src.deck.routes.db')
    @patch('src.cards.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_create_cards_deck_not_found(self, mock_cards_db, mock_deck_db, mock_auth):
        '''Test the error handling of createcards method'''
        mock_deck_db.child.return_value.push.side_effect = None
        response = self.client.post(
            '/deck/Test/card/create',
            data=json.dumps({
                'localId': 'Test',
                'cards': [{'front': 'front', 'back': 'back', 'hint': 'hint'}]
            })
        )
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Deck not found')

    @patch('src.auth.routes.auth')
    @patch('src.deck.routes.db')
    @patch('src.cards.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockBadAuth)
    async def test_create_cards_invalid_token(self, mock_cards_db, mock_deck_db, mock_auth):
        '''Test the error handling of createcards method'''
        response = self.client.post(
            '/deck/Test/card/create',
            data=json.dumps({
                'localId': 'Test',
                'cards': [{'front': 'front', 'back': 'back', 'hint': 'hint'}]
            })
        )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Invalid token')

    @patch('src.auth.routes.auth')
    @patch('src.deck.routes.db')
    @patch('src.cards.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_deck', return_value=True)
    async def test_update_card(self, mock_cards_db, mock_deck_db, mock_auth):
        '''Test the update card functionality'''
        response = self.client.patch(
            '/deck/test_deck/update/test_card',
            data=json.dumps({
                'word': 'updated_word',
                'meaning': 'updated_meaning'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Update Card Successful')

    @patch('src.auth.routes.auth')
    @patch('src.deck.routes.db')
    @patch('src.cards.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_deck', return_value=True)
    async def test_update_card_exception(self, mock_cards_db, mock_deck_db, mock_auth):
        '''Test error handling in update card functionality'''
        # Mock database to raise an exception
        mock_cards_db.child.return_value.order_by_child.return_value.equal_to.side_effect = Exception("Database error")

        response = self.client.patch(
            '/deck/test_deck/update/test_card',
            data=json.dumps({
                'word': 'updated_word',
                'meaning': 'updated_meaning'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertTrue('Update Card Failed' in data['message'])

    # @patch('src.auth.routes.auth')
    # @patch('src.deck.routes.db')
    # @patch('src.cards.routes.db')
    # def test_delete_card(self, mock_cards_db, mock_deck_db, mock_auth):
    #     '''Test the delete card functionality'''
    #     response = self.client.delete('/deck/test_deck/delete/test_card')
        
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.data)
    #     self.assertEqual(data['message'], 'Delete Card Successful')

    @patch('src.auth.routes.auth')
    @patch('src.deck.routes.db')
    @patch('src.cards.routes.db')
    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_deck', return_value=True)
    async def test_delete_card_exception(self, mock_cards_db, mock_deck_db, mock_auth):
        '''Test error handling in delete card functionality'''
        # Mock database to raise an exception
        mock_cards_db.child.return_value.order_by_child.return_value.equal_to.side_effect = Exception("Database error")

        response = self.client.delete('/deck/test_deck/delete/test_card')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Delete Card Failed')


    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.deck_is_visible', return_value=True)
    async def test_invalid_methods(self):
        '''Test invalid HTTP methods for routes'''
        # Test PUT method on card/all route
        response = self.client.put('/deck/Test/card/all')
        self.assertEqual(response.status_code, 405)

        # Test DELETE method on card/create route
        response = self.client.delete('/deck/Test/card/create')
        self.assertEqual(response.status_code, 405)

    @patch('src.__init__.get_user_id_from_request', return_value=mockBadAuth)
    async def test_delete_card_invalid_token(self):
        '''Test invalid HTTP methods for routes'''
        response = self.client.delete('/deck/Test/card/delete')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Invalid token')

    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_deck', return_value=mockUnauthorized)
    async def test_delete_card_unauthorized(self):
        '''Test invalid HTTP methods for routes'''
        response = self.client.delete('/deck/Test/card/delete')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Unauthorized')

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
    @patch('src.__init__.user_owns_deck', return_value=True)
    async def test_update_card_invalid_data(self):
        '''Test updating a card with invalid data'''
        response = self.client.patch(
            '/deck/test_deck/update/test_card',
            data=json.dumps({
                'word': '',
                'meaning': 'updated_meaning'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Invalid data provided')

    @patch('src.__init__.get_user_id_from_request', return_value=mockBadAuth)
    async def test_update_card_invalid_token(self):
        '''Test updating a card with invalid token'''
        response = self.client.patch(
            '/deck/test_deck/update/test_card',
            data=json.dumps({
                'word': '',
                'meaning': 'updated_meaning'
            })
        )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Invalid token')

    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_deck', return_value=mockUnauthorized)
    async def test_update_card_invalid_data(self):
        '''Test updating a card with invalid data'''
        response = self.client.patch(
            '/deck/test_deck/update/test_card',
            data=json.dumps({
                'word': '',
                'meaning': 'updated_meaning'
            })
        )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Unauthorized')



    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_deck', return_value=True)
    async def test_delete_card_non_existent(self):
        '''Test deleting a non-existent card'''
        response = self.client.delete('/deck/test_deck/delete/non_existent_card')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Card not found')

    @patch('src.__init__.get_user_id_from_request', return_value=mockBadAuth)
    async def test_delete_card_invalid_token(self):
        '''Test deleting a card with invalid token'''
        response = self.client.delete('/deck/test_deck/delete/invalid_token')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Invalid token')


    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_deck', return_value=mockUnauthorized)
    async def test_delete_card_invalid_token(self):
        '''Test deleting a card with invalid token'''
        response = self.client.delete('/deck/test_deck/delete/invalid_token')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Unauthorized')


    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    async def test_create_card_missing_fields(self):
        '''Test creating a card with missing fields'''
        response = self.client.post(
            '/deck/Test/card/create',
            data=json.dumps({
                'localId': 'Test',
                'cards': [{'front': '', 'back': 'back'}]
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Missing required fields')


    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_deck', return_value=True)
    async def test_update_card_non_existent_deck(self):
        '''Test updating a card in a non-existent deck'''
        response = self.client.patch(
            '/deck/non_existent_deck/update/test_card',
            data=json.dumps({
                'word': 'updated_word',
                'meaning': 'updated_meaning'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Deck not found')

    @patch('src.__init__.get_user_id_from_request', return_value=mockGoodAuth)
    @patch('src.__init__.user_owns_deck', return_value=True)
    async def test_delete_card_database_error(self):
        '''Test deleting a card with a database error'''
        with patch('src.cards.routes.db.child') as mock_db:
            mock_db.return_value.child.return_value.remove.side_effect = Exception("Database error")
            response = self.client.delete('/deck/test_deck/delete/test_card')
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            self.assertEqual(data['message'], 'Delete Card Failed')

if __name__ == "__main__":
    unittest.main()
