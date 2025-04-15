import { initializeApp } from 'firebase/app';
import { getDatabase } from "firebase/database";
import { getAuth } from "firebase/auth";

const firebaseConfig = {

}

export const app = initializeApp(firebaseConfig)
export const db = getDatabase(app)
export const auth = getAuth()