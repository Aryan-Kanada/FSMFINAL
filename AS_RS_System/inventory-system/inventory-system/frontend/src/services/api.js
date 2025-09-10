import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api';

// Create an axios instance with base URL
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add a response interceptor for better error handling
api.interceptors.response.use(
  response => response,
  error => {
    // Any status codes outside the range of 2xx cause this function to trigger
    const errorMessage = 
      error.response?.data?.message || 
      error.response?.data?.error || 
      error.message || 
      'An unknown error occurred';
    
    console.error('API Error:', errorMessage);
    
    return Promise.reject({
      ...error,
      message: errorMessage
    });
  }
);

export default api;
