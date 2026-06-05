import apiClient from './client';

export const pipelineAPI = {
  getHistory: async (examId, limit = 50, offset = 0) => {
    try {
      const response = await apiClient.get(`/api/pipeline/history/${examId}`, {
        params: { limit, offset }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get pipeline history:', error);
      return { history: [] };
    }
  },
  
  trigger: async (submissionId) => {
    try {
      const response = await apiClient.post(`/api/pipeline/process/${submissionId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to trigger pipeline:', error);
      throw error;
    }
  }
};


export default pipelineAPI;
