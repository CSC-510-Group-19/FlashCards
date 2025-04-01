import { getAuth, signInWithPopup, RecaptchaVerifier, signInWithPhoneNumber, OAuthProvider } from "firebase/auth";
import firebase from "firebase/compat";
import Auth = firebase.auth.Auth;

//In a global declaration file (e.g., globals.d.ts):
declare global {
  interface Window {
    recaptchaVerifier?: firebase.auth.RecaptchaVerifier;
    confirmationResult?: firebase.auth.ConfirmationResult;
  }
}

const auth = () => {
    const auth = getAuth()

    // method based on documentation example found in https://firebase.google.com/docs/auth/web/apple
    const oauthSignIn = (provider: OAuthProvider) => {
        // @ts-ignore
        signInWithPopup(auth, provider)
            .then((result) => {
                const user = result.user

                const credential = OAuthProvider.credentialFromResult(result)
                const accessToken = credential?.accessToken
                const idToken = credential?.idToken
                window.localStorage.setItem('flashCardUser', JSON.stringify(user));
            })
            .catch((error) => {
                console.log("Error " + error.code + ": " + error.message)
            })
    }
}

export default auth;