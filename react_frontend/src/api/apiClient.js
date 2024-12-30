// apiClient.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: `${process.env.REACT_APP_API_URL}`,
});

// Request interceptor to add the access token to headers
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${process.env.REACT_APP_API_URL}/refresh`, null, {
          headers: {
            'Authorization': `Bearer ${refreshToken}`,
          },
        });
        const newAccessToken = response.data.access_token;
        localStorage.setItem('access_token', newAccessToken);
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Handle refresh token expiration (e.g., redirect to login)
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;