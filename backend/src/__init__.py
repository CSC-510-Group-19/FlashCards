import pyrebase

config = {
  'apiKey': "AIzaSyCl9E0bQzdDwge6nQeF9w2iCUU4jQ4b7rI",
  'authDomain': "flashcards-swe.firebaseapp.com",
  'databaseURL': "https://flashcards-swe-default-rtdb.firebaseio.com/",
  'projectId': "flashcards-swe",
  'storageBucket': "flashcards-swe.firebasestorage.app",
  'messagingSenderId': "35839497511",
  'appId': "1:35839497511:web:ef0112f59ad872339dc502",
  'measurementId': "G-FP98B3FHXW"
}

firebase = pyrebase.initialize_app(config)