import axios from './axios';

// Register a new user
export const registerUser = async (userData) => {
  // userData = { email, password, firstname, lastname, institution }
  return axios.post('/register', userData);
};

// Login user
export const loginUser = async (credentials) => {
  // credentials = { email, password }
  return axios.post('/login', credentials);
};

// Refresh token (optional usage if you want a direct call)
export const refreshToken = async () => {
  return axios.post('/refresh', {});
};

// Logout user
export const logoutUser = async (token) => {
  return axios.post('/logout', {}, {
    headers: {
      Authorization: `Bearer ${token}`, // Pass the JWT as a Bearer token
    },
  });
};