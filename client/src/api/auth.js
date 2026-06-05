import apiClient from './client';

/**
 * Auth API endpoints
 */
export const authAPI = {
  /**
   * Login user with email and password
   * Returns: { access_token, user: { id, email, role } }
   */
  login: async (email, password) => {
    const response = await apiClient.post('/api/auth/login', { email, password });
    return response.data;
  },

  /**
   * Register new user
   */
  register: async (email, password, role) => {
    const response = await apiClient.post('/api/auth/register', { email, password, role });
    return response.data;
  },

  /**
   * Logout user
   */
  logout: async () => {
    const response = await apiClient.post('/api/auth/logout');
    return response.data;
  },

  /**
   * Get current user info
   */
  getCurrentUser: async () => {
    const response = await apiClient.get('/api/auth/me');
    return response.data;
  },
};

export default authAPI;
