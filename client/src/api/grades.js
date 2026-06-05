import apiClient from './client';

/**
 * Grade API endpoints - Used by TAs for review and approval
 */
export const gradesAPI = {
  /**
   * Get pending grades queue for TA review
   */
  getQueue: async (examId, priority = null, limit = 50, offset = 0) => {
    const response = await apiClient.get('/api/grades/queue', {
      params: { exam_id: examId, priority, limit, offset },
    });
    return response.data;
  },

  /**
   * Get grade by ID
   */
  getGrade: async (gradeId) => {
    const response = await apiClient.get(`/api/grades/${gradeId}`);
    return response.data;
  },

  /**
   * Get exam grading statistics
   */
  getExamStats: async (examId) => {
    const response = await apiClient.get(`/api/grades/${examId}/stats`);
    return response.data;
  },

  /**
   * Approve a grade
   */
  approveGrade: async (gradeId, feedback = null) => {
    const response = await apiClient.patch(`/api/grades/${gradeId}/approve`, {
      feedback,
    });
    return response.data;
  },

  /**
   * Override a grade (TA changes the score)
   */
  overrideGrade: async (gradeId, overrideData) => {
    const response = await apiClient.patch(`/api/grades/${gradeId}/override`, overrideData);
    return response.data;
  },

  /**
   * Get grades for an answer region
   */
  getGradesByAnswerRegion: async (answerRegionId) => {
    const response = await apiClient.get(`/api/grades/answer-region/${answerRegionId}`);
    return response.data;
  },
};

export default gradesAPI;
