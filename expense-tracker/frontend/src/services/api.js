import axios from 'axios';

// Create a configured Axios instance
const api = axios.create({
  baseURL: '/api', // Proxied by Vite to the backend
  withCredentials: true, // Crucial for sending/receiving HttpOnly cookies
});

// We need a way to dynamically inject the token from our React state
// without causing circular dependencies with the AuthContext.
// We'll set this from inside the AuthProvider.
let accessToken = null;

export const setAccessToken = (token) => {
  accessToken = token;
};

// Request Interceptor: Attach the access token to every request
api.interceptors.request.use(
  (config) => {
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401s and automatic token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If the error is 401 and we haven't already retried
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Prevent infinite loops if the refresh endpoint itself returns 401
      if (originalRequest.url === '/auth/refresh') {
        return Promise.reject(error);
      }

      originalRequest._retry = true;

      try {
        // Attempt to refresh the token using the HttpOnly cookie
        const response = await axios.post('/api/auth/refresh', {}, {
          withCredentials: true // Ensure cookie is sent
        });

        const newAccessToken = response.data.access_token;
        setAccessToken(newAccessToken);

        // Retry the original request with the new token
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed (e.g. cookie expired)
        // The AuthContext will catch this and clear the user state
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export const expensesApi = {
  getAll: (skip = 0, limit = 50, categoryId = null) => {
    let url = `/expenses?skip=${skip}&limit=${limit}`;
    if (categoryId) url += `&category_id=${categoryId}`;
    return api.get(url);
  },
  getById: (id) => api.get(`/expenses/${id}`),
  create: (data) => api.post('/expenses', data),
  update: (id, data) => api.put(`/expenses/${id}`, data),
  delete: (id) => api.delete(`/expenses/${id}`),
};

export const categoriesApi = {
  getAll: () => api.get('/categories'),
  create: (data) => api.post('/categories', data),
  delete: (id) => api.delete(`/categories/${id}`),
};

export default api;
