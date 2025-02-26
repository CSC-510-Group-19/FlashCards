import unittest
from flask import Flask
from unittest.mock import patch
from src.api import create_app  # Import the create_app function from your main module

class TestCreateApp(unittest.TestCase):
    
    def setUp(self):
        """Setup test client for Flask app."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

    def test_app_instance(self):
        """Test that create_app returns a Flask instance."""
        self.assertIsInstance(self.app, Flask)

    def test_blueprints_registration(self):
        """Test that all blueprints are registered."""
        blueprint_names = ['auth_bp', 'deck_bp', 'card_bp', 'folder_bp']
        
        for bp_name in blueprint_names:
            self.assertIn(bp_name, self.app.blueprints, f"{bp_name} should be registered in the app")

    def test_app_custom_config(self):
        '''Test the app instance with custom configuration'''
        app = create_app({'TESTING': True})
        self.assertTrue(app.config['TESTING'])

    def test_app_missing_blueprints(self):
        '''Test the app instance with missing blueprints'''
        app = Flask(__name__)
        with self.assertRaises(KeyError):
            app.blueprints['auth_bp']

    def test_app_invalid_route(self):
        '''Test accessing an invalid route'''
        response = self.client.get('/invalid-route')
        self.assertEqual(response.status_code, 404)

    def test_app_middleware(self):
        '''Test that middleware is applied'''
        app = create_app()
        @app.errorhandler(404)
        def handle_not_found(e):
            return 'Not Found', 404
        response = app.test_client().get('/invalid-route')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.decode(), 'Not Found')

    def test_app_environment_variables(self):
        '''Test the app instance with environment variables'''
        import os
        os.environ['FLASK_ENV'] = 'development'
        app = create_app()
        self.assertEqual(app.config['ENV'], 'development')

if __name__ == '__main__':
    unittest.main()
