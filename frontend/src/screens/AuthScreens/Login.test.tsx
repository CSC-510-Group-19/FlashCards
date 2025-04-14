import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Login from "./Login";
import OAuthOptions from "components/OAuthOptions";
import http from "utils/api";
import { MemoryRouter } from "react-router-dom";
import Swal from "sweetalert2";
import Register from "./Register";

// Mocks
jest.mock("utils/api");
jest.mock("sweetalert2", () => ({
  fire: jest.fn(),
}));



jest.mock("firebase/auth", () => {
  const actualAuth = jest.requireActual("firebase/auth");
  return {
    ...actualAuth,
    getAuth: jest.fn(() => ({})),
    signInWithPopup: jest.fn(),
    GoogleAuthProvider: jest.fn(),
    GithubAuthProvider: jest.fn(),
    FacebookAuthProvider: jest.fn(),

    
  };
});

import * as AuthApi from "../../api/auth";

beforeAll(() => {
  Object.defineProperty(window, "localStorage", {
    value: {
      setItem: jest.fn(),
      getItem: jest.fn(() => null),
      removeItem: jest.fn(),
      clear: jest.fn(),
    },
    writable: true,
  });
});

import { FacebookAuthProvider, getAuth, GithubAuthProvider, GoogleAuthProvider, signInWithPopup } from "firebase/auth";

describe("Login Component", () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  test("renders login form with email, password, and login button", () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    expect(screen.getByLabelText(/Email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Login/i })).toBeInTheDocument();
  });

  test("displays 'Logging in...' when isSubmitting is true", async () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    const emailInput = screen.getByLabelText(/Email address/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    const loginButton = screen.getByRole("button", { name: /Login/i });

    userEvent.type(emailInput, "test@example.com");
    userEvent.type(passwordInput, "password123");

    (http.post as jest.Mock).mockResolvedValue({
      data: { user: { name: "Test User" } },
    });

    userEvent.click(loginButton);

    expect(loginButton).toHaveTextContent("Logging in...");
    await waitFor(() => expect(loginButton).toHaveTextContent("Login"));
  });

  test("handles successful login", async () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    const emailInput = screen.getByLabelText(/Email address/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    const loginButton = screen.getByRole("button", { name: /Login/i });

    userEvent.type(emailInput, "test@example.com");
    userEvent.type(passwordInput, "password123");

    (http.post as jest.Mock).mockResolvedValue({
      data: { user: { name: "Test User" } },
    });

    userEvent.click(loginButton);

    await waitFor(() => {
      expect(window.localStorage.setItem).toHaveBeenCalledWith(
        "flashCardUser",
        JSON.stringify({ name: "Test User" })
      );
      expect(Swal.fire).toHaveBeenCalledWith(
        expect.objectContaining({
          icon: "success",
          title: "Login Successful!",
          text: "You have successfully logged in",
        })
      );
    });
  });

  test("handles login failure", async () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    const emailInput = screen.getByLabelText(/Email address/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    const loginButton = screen.getByRole("button", { name: /Login/i });

    userEvent.type(emailInput, "wrong@example.com");
    userEvent.type(passwordInput, "wrongpassword");

    (http.post as jest.Mock).mockRejectedValue(new Error("Login Failed"));

    userEvent.click(loginButton);

    await waitFor(() => {
      expect(Swal.fire).toHaveBeenCalledWith(
        expect.objectContaining({
          icon: "error",
          title: "Login Failed!",
          text: "An error occurred, please try again",
        })
      );
    });
  });

  test("renders oauth options in login", () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    const images = screen.getAllByRole("img");
    expect(images).toHaveLength(3);

    expect(screen.getByAltText("GitHub Login")).toBeInTheDocument();
    expect(screen.getByAltText("Google Login")).toBeInTheDocument();
    expect(screen.getByAltText("Apple Login")).toBeInTheDocument();
  });

  test("renders oauth options in register", () => {
    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    const images = screen.getAllByRole("img");
    expect(images).toHaveLength(3);

    expect(screen.getByAltText("GitHub Login")).toBeInTheDocument();
    expect(screen.getByAltText("Google Login")).toBeInTheDocument();
    expect(screen.getByAltText("Apple Login")).toBeInTheDocument();
  });

  test('calls signInWithProvider with "github" when GitHub image is clicked', () => {
    const spy = jest.spyOn(AuthApi, "signInWithProvider").mockImplementation(jest.fn());
    render(<OAuthOptions />);
    fireEvent.click(screen.getByAltText("GitHub Login"));
    expect(AuthApi.signInWithProvider).toHaveBeenCalledWith("github");
    spy.mockRestore();
  });

  test('calls signInWithProvider with "google" when Google image is clicked', () => {
    const spy = jest.spyOn(AuthApi, "signInWithProvider").mockImplementation(jest.fn());
    render(<OAuthOptions />);
    fireEvent.click(screen.getByAltText("Google Login"));
    expect(AuthApi.signInWithProvider).toHaveBeenCalledWith("google");
    spy.mockRestore();
  });

  test('calls signInWithProvider with "facebook" when Apple image is clicked', () => {
    const spy = jest.spyOn(AuthApi, "signInWithProvider").mockImplementation(jest.fn());
    render(<OAuthOptions />);
    fireEvent.click(screen.getByAltText("Apple Login"));
    expect(AuthApi.signInWithProvider).toHaveBeenCalledWith("facebook");
    spy.mockRestore();
  });
});

describe("signInWithProvider function", () => {
  let originalLocation: Location;

  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();

    Object.defineProperty(window, "location", {
      value: { reload: jest.fn() },
      writable: true,
    });

    (getAuth as jest.Mock).mockReturnValue({ currentUser: null });
    (signInWithPopup as jest.Mock).mockReset();
  });

  test("successfully signs in with GitHub provider and reloads page", async () => {
    const mockUser = {
      uid: "github123",
      email: "test@github.com",
      displayName: "GitHub User",
      photoURL: "https://github.com/profile.jpg",
      emailVerified: true,
      getIdToken: jest.fn().mockResolvedValue("mock-token"),
      refreshToken: "mock-refresh-token",
      providerId: "github.com",
    };

    (signInWithPopup as jest.Mock).mockResolvedValue({
      user: mockUser,
      providerId: "github.com",
      operationType: "signIn",
    });

    await AuthApi.signInWithProvider("github");

    expect(getAuth).toHaveBeenCalled();
    expect(signInWithPopup).toHaveBeenCalledWith(
      expect.anything(),
      expect.any(GithubAuthProvider)
    );

    expect(window.localStorage.setItem).toHaveBeenCalledWith(
      "flashCardUser",
      expect.stringContaining("github123")
    );

    expect(window.location.reload).toHaveBeenCalled();
  });

  test("successfully signs in with Facebook provider and reloads page", async () => {
    const mockUser = {
      uid: "facebook123",
      email: "test@github.com",
      displayName: "Facebook User",
      photoURL: "https://github.com/profile.jpg",
      emailVerified: true,
      getIdToken: jest.fn().mockResolvedValue("mock-token"),
      refreshToken: "mock-refresh-token",
      providerId: "facebook.com",
    };

    (signInWithPopup as jest.Mock).mockResolvedValue({
      user: mockUser,
      providerId: "facebook.com",
      operationType: "signIn",
    });

    await AuthApi.signInWithProvider("facebook");

    expect(getAuth).toHaveBeenCalled();
    expect(signInWithPopup).toHaveBeenCalledWith(
      expect.anything(),
      expect.any(FacebookAuthProvider)
    );

    expect(window.localStorage.setItem).toHaveBeenCalledWith(
      "flashCardUser",
      expect.stringContaining("facebook123")
    );

    expect(window.location.reload).toHaveBeenCalled();
  });

  test("successfully signs in with Google provider and reloads page", async () => {
    const mockUser = {
      uid: "google123",
      email: "test@google.com",
      displayName: "Google User",
      photoURL: "https://github.com/profile.jpg",
      emailVerified: true,
      getIdToken: jest.fn().mockResolvedValue("mock-token"),
      providerId: "google.com",
    };

    (signInWithPopup as jest.Mock).mockResolvedValue({
      user: mockUser,
      providerId: "google.com",
      operationType: "signIn",
    });

    await AuthApi.signInWithProvider("google");

    expect(getAuth).toHaveBeenCalled();
    expect(signInWithPopup).toHaveBeenCalledWith(
      expect.anything(),
      expect.any(GoogleAuthProvider)
    );

    expect(window.localStorage.setItem).toHaveBeenCalledWith(
      "flashCardUser",
      expect.stringContaining("google123")
    );

    expect(window.location.reload).toHaveBeenCalled();
  });

  test("handles account-exists-with-different-credential error when signing in with GitHub", async () => {

    const mockError = {
      code: 'auth/account-exists-with-different-credential',
      customData: { email: 'test@example.com' },
      message: 'Account exists with different credential'
    };
    
    (signInWithPopup as jest.Mock).mockImplementation(() => Promise.reject(mockError));
    
    const swalSpy = jest.spyOn(Swal, 'fire').mockImplementation(() => Promise.resolve({} as any));
    
    AuthApi.signInWithProvider("github");
    
    await new Promise(process.nextTick);
    
    expect(swalSpy).toHaveBeenCalledWith({
      icon: 'error',
      title: `Email test@example.com already exists with a different provider`,
      text: 'Try again with that provider.',
      confirmButtonColor: '#221daf',
    });
  });
  
  test("handles account-exists-with-different-credential error when signing in with Google", async () => {
    const mockError = {
      code: 'auth/account-exists-with-different-credential',
      customData: { email: 'test@example.com' },
      message: 'Account exists with different credential'
    };
    
    (signInWithPopup as jest.Mock).mockImplementation(() => Promise.reject(mockError));
    
    const swalSpy = jest.spyOn(Swal, 'fire').mockImplementation(() => Promise.resolve({} as any));
    
    AuthApi.signInWithProvider("google");
    
    await new Promise(process.nextTick);
    
    expect(swalSpy).toHaveBeenCalledWith({
      icon: 'error',
      title: `Email test@example.com already exists with a different provider`,
      text: 'Try again with that provider.',
      confirmButtonColor: '#221daf',
    });
  });
  
  test("handles account-exists-with-different-credential error when signing in with Facebook", async () => {
    
    const mockError = {
      code: 'auth/account-exists-with-different-credential',
      customData: { email: 'test@example.com' },
      message: 'Account exists with different credential'
    };
    
    (signInWithPopup as jest.Mock).mockImplementation(() => Promise.reject(mockError));
    
    const swalSpy = jest.spyOn(Swal, 'fire').mockImplementation(() => Promise.resolve({} as any));
    
    AuthApi.signInWithProvider("facebook");
    
    await new Promise(process.nextTick);
    
    expect(swalSpy).toHaveBeenCalledWith({
      icon: 'error',
      title: `Email test@example.com already exists with a different provider`,
      text: 'Try again with that provider.',
      confirmButtonColor: '#221daf',
    });
  });
  
  test("handles pop up closing", async () => {
    const mockError = {
      code: 'auth/popup-closed-by-user',
      message: 'The popup has been closed by the user before finalizing the operation.'
    };
    
    (signInWithPopup as jest.Mock).mockImplementation(() => Promise.reject(mockError));
    
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});
    
    AuthApi.signInWithProvider("github");
    
    await new Promise(process.nextTick);
    
    expect(consoleErrorSpy).toHaveBeenCalledWith("Auth error code:", mockError.code);
    expect(consoleErrorSpy).toHaveBeenCalledWith("Auth error message:", mockError.message);
    
    expect(alertSpy).toHaveBeenCalledWith(`Sign in failed: ${mockError.message}`);
  });

  test("handles popup-blocked error when signing in with Google", async () => {
    const mockError = {
      code: 'auth/popup-blocked',
      message: 'Popup has been blocked by the browser'
    };
    
    (signInWithPopup as jest.Mock).mockImplementation(() => Promise.reject(mockError));
    
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});
    
    AuthApi.signInWithProvider("google");
    
    await new Promise(process.nextTick);
    
    expect(consoleErrorSpy).toHaveBeenCalledWith("Auth error code:", mockError.code);
    expect(consoleErrorSpy).toHaveBeenCalledWith("Auth error message:", mockError.message);
    
    expect(alertSpy).toHaveBeenCalledWith(`Sign in failed: ${mockError.message}`);
  });
  
  test("handles network timeout error when signing in with Facebook", async () => {
    const mockError = {
      code: 'auth/network-request-failed',
      message: 'A network error has occurred'
    };
    
    (signInWithPopup as jest.Mock).mockImplementation(() => Promise.reject(mockError));
    
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});
    
    AuthApi.signInWithProvider("facebook");
    
    await new Promise(process.nextTick);
    
    expect(consoleErrorSpy).toHaveBeenCalledWith("Auth error code:", mockError.code);
    expect(alertSpy).toHaveBeenCalledWith(`Sign in failed: ${mockError.message}`);
  });
  
  test("handles when user cancels authentication process with GitHub", async () => {
    const mockError = {
      code: 'auth/cancelled-popup-request',
      message: 'The popup has been closed by the user before finalizing the operation'
    };
    
    (signInWithPopup as jest.Mock).mockImplementation(() => Promise.reject(mockError));
    
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});
    
    AuthApi.signInWithProvider("github");
    
    await new Promise(process.nextTick);
    
    expect(consoleErrorSpy).toHaveBeenCalledWith("Auth error code:", mockError.code);
    expect(alertSpy).toHaveBeenCalledWith(`Sign in failed: ${mockError.message}`);
  });
  
  test("handles unexpected error during provider creation", async () => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
    const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});
    
    (GoogleAuthProvider as unknown as jest.Mock).mockImplementation(() => {
      throw new Error("Unexpected provider error");
    });
    
    AuthApi.signInWithProvider("google");
    
    await new Promise(process.nextTick);
    
    expect(alertSpy).toHaveBeenCalledWith("Authentication error occurred. Check console for details.");
  });
  
  test("catches error when localStorage is not available", async () => {
    const mockUser = {
      uid: "google123",
      email: "test@google.com",
      displayName: "Google User",
      photoURL: "https://example.com/photo.jpg",
      emailVerified: true,
      getIdToken: jest.fn().mockResolvedValue("mock-token")
    };
    
    (signInWithPopup as jest.Mock).mockResolvedValue({
      user: mockUser,
      providerId: "google.com",
      operationType: "signIn"
    });
    
    const originalSetItem = window.localStorage.setItem;
    (window.localStorage.setItem as jest.Mock).mockImplementation(() => {
      throw new Error("Storage quota exceeded");
    });
    
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    AuthApi.signInWithProvider("twitter");
    
    await new Promise(process.nextTick);
    
    expect(consoleErrorSpy).toHaveBeenCalled();
    
    window.localStorage.setItem = originalSetItem;
  });

  test("handles invalid OAuth token during authentication process", async () => {
    const mockError = {
      code: 'auth/invalid-credential',
      message: 'Unsupported provider'
    };
    
    (signInWithPopup as jest.Mock).mockImplementation(() => Promise.reject(mockError));
    
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});
    
    AuthApi.signInWithProvider("google");
    
    await new Promise(process.nextTick);
    
    expect(consoleErrorSpy).toHaveBeenCalledWith("Auth error code:", mockError.code);
    expect(alertSpy).toHaveBeenCalledWith(`Sign in failed: ${mockError.message}`);
  });
  
  test("handles provider's API permission errors", async () => {
    const mockError = {
      code: 'auth/insufficient-permission',
      message: 'Application does not have permission to access requested scopes',
      providerId: 'github.com'
    };
    
    (signInWithPopup as jest.Mock).mockImplementation(() => Promise.reject(mockError));
    
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});
    
    AuthApi.signInWithProvider("github");
    
    await new Promise(process.nextTick);
    
    expect(consoleErrorSpy).toHaveBeenCalledWith("Auth error code:", mockError.code);
    expect(consoleErrorSpy).toHaveBeenCalledWith("Auth error message:", mockError.message);
    expect(alertSpy).toHaveBeenCalledWith(`Sign in failed: ${mockError.message}`);
  });
  
  test("handles provider-specific operation-not-allowed error", async () => {
    const mockError = {
      code: 'auth/operation-not-allowed',
      message: 'The Facebook authentication provider is disabled for this Firebase project',
      providerId: 'facebook.com'
    };
    
    (signInWithPopup as jest.Mock).mockImplementation(() => Promise.reject(mockError));
    
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});
    
    AuthApi.signInWithProvider("facebook");
    
    await new Promise(process.nextTick);
    
    expect(consoleErrorSpy).toHaveBeenCalledWith("Auth error code:", mockError.code);
    expect(consoleErrorSpy).toHaveBeenCalledWith("Auth error message:", mockError.message);
    expect(alertSpy).toHaveBeenCalledWith(`Sign in failed: ${mockError.message}`);
  });
  
});
