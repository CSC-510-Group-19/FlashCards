import { initializeApp } from 'firebase/app';
import { getDatabase } from "firebase/database";

const firebaseConfig = {
  'apiKey': "AIzaSyAPXpHYZpD5DNjsg6XAEhTVA5V9kA5rNWY",
  'authDomain': "flashcards-93088.firebaseapp.com",
  'databaseURL': "https://flashcards-93088-default-rtdb.firebaseio.com",
  'projectId': "flashcards-93088",
  'storageBucket': "flashcards-93088.firebasestorage.app",
  'messagingSenderId': "457073208752",
  'appId': "457073208752:web:0c6e9eaea7740d4a387a75"
}

export const app = initializeApp(firebaseConfig)
export const db = getDatabase(app)