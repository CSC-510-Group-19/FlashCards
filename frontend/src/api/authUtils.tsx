import { getAuth, signInWithPopup, RecaptchaVerifier, signInWithPhoneNumber, OAuthProvider } from "firebase/auth";
import firebase from "firebase/compat";
import '../initializeFirebase';
import {Exception} from "sass";
import http from "../utils/api";

//In a global declaration file (e.g., globals.d.ts):
declare global {
  interface Window {
    recaptchaVerifier?: firebase.auth.RecaptchaVerifier;
    confirmationResult?: firebase.auth.ConfirmationResult;
  }
}
