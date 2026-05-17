import apiClient from './client';

export const systemAPI = {
  getHealth: async () => {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('Failed to check system health:', error);
      return { status: 'error', services: {} };
    }
  }
};

export default systemAPI;
