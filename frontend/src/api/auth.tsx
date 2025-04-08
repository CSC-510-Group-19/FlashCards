import { getAuth, signInWithPopup, RecaptchaVerifier, signInWithPhoneNumber, OAuthProvider, GoogleAuthProvider, GithubAuthProvider } from "firebase/auth";
import firebase from 'firebase/compat/app';
import Auth = firebase.auth.Auth;

//In a global declaration file (e.g., globals.d.ts):
declare global {
  interface Window {
    recaptchaVerifier?: firebase.auth.RecaptchaVerifier;
    confirmationResult?: firebase.auth.ConfirmationResult;
  }
}

export const signInWithProvider = (providerName: 'google' | 'github' | 'apple') => {
  const auth = getAuth();
  let provider;

  switch (providerName) {
    case 'google':
      provider = new GoogleAuthProvider();
      break;
    case 'github':
      provider = new GithubAuthProvider();
      break;
    case 'apple':
      provider = new OAuthProvider('apple.com');
      break;
    default:
      throw new Error("Unsupported provider");
  }

  signInWithPopup(auth, provider)
    .then((result) => {
      const user = result.user;
      window.localStorage.setItem('flashCardUser', JSON.stringify(user));
      console.log("User signed in:", user);
    })
    .catch((error) => {
      console.error("Auth error:", error.code, error.message);
    });
};