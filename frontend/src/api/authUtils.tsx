import { getAuth, signInWithPopup, RecaptchaVerifier, signInWithPhoneNumber, OAuthProvider } from "firebase/auth";
import firebase from "firebase/compat";
import Auth = firebase.auth.Auth;
import User = firebase.User;

//In a global declaration file (e.g., globals.d.ts):
declare global {
  interface Window {
    recaptchaVerifier?: firebase.auth.RecaptchaVerifier;
    confirmationResult?: firebase.auth.ConfirmationResult;
  }
}

const auth = getAuth()

// method based on documentation example found in https://firebase.google.com/docs/auth/web/apple
export const oauthSignIn = (provider: OAuthProvider) => {
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

export const getAuthToken = () => {
    const user = auth.currentUser;
    let token :String =  "";
    if (user) {
        user.getIdToken().then((idToken : String) => {
            token = idToken;
        }).catch((error) => {
            console.error("Error retrieving Authorization token: ", error);
        });
    } else {
        console.error("User is not signed in");
    }
    return token;
}