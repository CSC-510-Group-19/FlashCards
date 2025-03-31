import { getAuth, RecaptchaVerifier, signInWithPhoneNumber } from "firebase/auth";
import firebase from "firebase/compat";

//In a global declaration file (e.g., globals.d.ts):
declare global {
  interface Window {
    recaptchaVerifier?: firebase.auth.RecaptchaVerifier;
    confirmationResult?: firebase.auth.ConfirmationResult;
  }
}

const auth = () => {
    const auth = getAuth()
    const phoneLoginSignUp = (phoneNumber: String) => {
        window.recaptchaVerifier = new RecaptchaVerifier(auth, 'recaptcha-container', {
          'size': 'invisible',
          'callback': (response: any) => {
           //onSignInSubmit();
          },
          'expired-callback': () => {
            // Response expired. Ask user to solve reCAPTCHA again.
            // ...
          }
        });

        // @ts-ignore
        signInWithPhoneNumber(auth, phoneNumber, window.recaptchaVerifier)
            .then((confirmationResult: any) => {
              // SMS sent. Prompt user to type the code from the message, then sign the
              // user in with confirmationResult.confirm(code).
              window.confirmationResult = confirmationResult;
              // ...
            }).catch((error) => {

            });
    }
}

export default auth;