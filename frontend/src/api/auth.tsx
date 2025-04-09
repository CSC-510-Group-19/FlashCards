import { getAuth, signInWithPopup, GithubAuthProvider, OAuthProvider, GoogleAuthProvider } from "firebase/auth";
import '../initializeFirebase'; 

export const signInWithProvider = (providerName: 'google' | 'github' | 'apple') => {
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
      case 'apple':
        provider = new OAuthProvider('apple.com');
        break;
      default:
        throw new Error("Unsupported provider");
    }
    
    console.log("Provider created, attempting sign in");
    
    signInWithPopup(auth, provider)
      .then((result) => {
        console.log("Sign in successful");
        const user = result.user;
        window.localStorage.setItem('flashCardUser', JSON.stringify(user));
        console.log("User signed in:", user);
        window.location.reload(); // Optional: refresh page after login
      })
      .catch((error) => {
        console.error("Auth error code:", error.code);
        console.error("Auth error message:", error.message);
        console.error("Full error:", error);
        alert(`Sign in failed: ${error.message}`);
      });
  } catch (error) {
    console.error("Exception in signInWithProvider:", error);
    alert("Authentication error occurred. Check console for details.");
  }
};