import axios, { AxiosInstance } from 'axios'
import {getAuth, getIdToken, User} from "firebase/auth";
import '../initializeFirebase'

const baseURL = 'http://127.0.0.1:5000/'

const http: AxiosInstance = axios.create({
  baseURL,
})

http.defaults.headers.post['Content-Type'] = 'application/json';

const auth = getAuth()
export const getAuthToken = async (user: User) => {
    try {
      return await getIdToken(user);
  } catch (error) {
    console.error("Error getting ID token:", error);
    throw error;
  }
}
http.interceptors.request.use(
  async (config) => {
    // Get the current user
    const user = auth.currentUser;

    // If a user is signed in, get the token and attach it to the header
    if (user) {
      const token = await getIdToken(user);
      config.headers.Authorization = `${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
)

export default http