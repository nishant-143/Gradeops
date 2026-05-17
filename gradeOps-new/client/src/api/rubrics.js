import apiClient from './client';

/**
 * Rubric API endpoints
 */
export const rubricsAPI = {
  /**
   * List rubrics
   */
  listRubrics: async (limit = 20, offset = 0) => {
    const response = await apiClient.get('/api/rubrics', {
      params: { limit, offset },
    });
    return response.data;
  },

  /**
   * Get rubric by Exam ID
   */
  getRubricByExam: async (examId) => {
    const response = await apiClient.get(`/api/rubrics/${examId}`);
    return response.data;
  },

  /**
   * Create new rubric
   */
  createRubric: async (examId, rubricData) => {
    const response = await apiClient.post('/api/rubrics', rubricData, {
      params: { exam_id: examId },
    });
    return response.data;
  },

  /**
   * Update rubric
   */
  updateRubric: async (rubricId, rubricData) => {
    const response = await apiClient.put(`/api/rubrics/${rubricId}`, rubricData);
    return response.data;
  },

  /**
   * Delete rubric
   */
  deleteRubric: async (rubricId) => {
    const response = await apiClient.delete(`/api/rubrics/${rubricId}`);
    return response.data;
  },
};

export default rubricsAPI;
