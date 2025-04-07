import axios, { AxiosInstance } from 'axios'
import {getAuthToken} from '../api/authUtils'

const baseURL = 'http://127.0.0.1:5000/'

const http: AxiosInstance = axios.create({
  baseURL,
})

http.defaults.headers.post['Content-Type'] = 'application/json';
http.defaults.headers.common['Authorization'] = 'Bearer ' + getAuthToken();

export default http