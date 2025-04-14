import { getAuth, signInWithPopup, GithubAuthProvider, OAuthProvider, GoogleAuthProvider, FacebookAuthProvider } from "firebase/auth";
import '../initializeFirebase';
import Swal from "sweetalert2";

export const signInWithProvider = (providerName: 'google' | 'github' | 'facebook') => {
  console.log(`Starting authentication with ${providerName}`);
  
  try {
    const auth = getAuth();
    console.log("Auth object:", auth);
    
    let provider;

    switch (providerName) {
      case 'google':
        console.log("Creating Google provider");
        provider = new GoogleAuthProvider();
        break;
      case 'github':
        console.log("Creating GitHub provider");
        provider = new GithubAuthProvider();
        break;
      case 'facebook':
        provider = new FacebookAuthProvider();
        break;
      default:
        throw new Error("Unsupported provider");
    }
    
    console.log("Provider created, attempting sign in");
    
    signInWithPopup(auth, provider)
      .then((result) => {
        console.log("Sign in successful");
        const firebaseUser = result.user;

         // Extract relevant user data in the same format as your backend returns
         const user = {
          localId: firebaseUser.uid,
          email: firebaseUser.email,
          displayName: firebaseUser.displayName,
          photoURL: firebaseUser.photoURL,
          // Add any other fields your backend provides
          providerId: providerName,
          // If your backend user object needs these:
          emailVerified: firebaseUser.emailVerified,
          // Add a token if your backend expects it for verification
          idToken: firebaseUser.getIdToken ? firebaseUser.getIdToken() : null
        };
        

        window.localStorage.setItem('flashCardUser', JSON.stringify(user));
        console.log("User signed in:", user);
        window.location.reload(); // Optional: refresh page after login
      })
      .catch((error) => {
        // Handle the account-exists-with-different-credential error
        if (error.code === 'auth/account-exists-with-different-credential') {
          const email = error.customData?.email;
          Swal.fire({
                    icon: 'error',
                    title: `Email ${email} already exists with a different provider`,
                    text: 'Try again with that provider.',
                    confirmButtonColor: '#221daf',
                  })
        console.log(`Email ${email} already exists with a different provider`);
        } else {
          console.error("Auth error code:", error.code);
          console.error("Auth error message:", error.message);
          console.error("Full error:", error);
          alert(`Sign in failed: ${error.message}`);
        }
        
      });
  } catch (error) {
    console.error("Exception in signInWithProvider:", error);
    alert("Authentication error occurred. Check console for details.");
  }
};