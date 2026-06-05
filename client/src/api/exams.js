import apiClient from './client';
import { useAuthStore } from '../store/authStore';

/**
 * Exam API endpoints
 */
export const examsAPI = {
  /**
   * List all exams for current user
   */
  listExams: async (limit = 20, offset = 0) => {
    const { user, role } = useAuthStore.getState();
    const params = { limit, offset };
    
    // Instructors only see their own exams, TAs can see everything
    if (role === 'instructor' && user?.id) {
      params.instructor_id = user.id;
    }
    
    const response = await apiClient.get('/api/exams', { params });
    return response.data;
  },

  /**
   * Get exam by ID
   */
  getExam: async (examId) => {
    const response = await apiClient.get(`/api/exams/${examId}`);
    return response.data;
  },

  /**
   * Create new exam
   */
  createExam: async (title) => {
    const user = useAuthStore.getState().user;
    const response = await apiClient.post('/api/exams', 
      { title },
      {
        params: {
          instructor_id: user?.id,
        }
      }
    );
    return response.data;
  },

  /**
   * Update exam
   */
  updateExam: async (examId, updates) => {
    const response = await apiClient.patch(`/api/exams/${examId}`, updates);
    return response.data;
  },

  /**
   * Delete exam
   */
  deleteExam: async (examId) => {
    const response = await apiClient.delete(`/api/exams/${examId}`);
    return response.data;
  },

  /**
   * Get exam stats (for instructor dashboard)
   */
  getExamStats: async (examId) => {
    const response = await apiClient.get(`/api/exams/${examId}/stats`);
    return response.data;
  },

  /**
   * Export grades as CSV
   */
  exportCSV: async (examId, includeJustifications = true, includePlagiarism = true) => {
    const response = await apiClient.get(`/api/export/${examId}/csv`, {
      params: { 
        include_justifications: includeJustifications,
        include_plagiarism: includePlagiarism
      },
      responseType: 'blob' // Important to receive binary data
    });
    return response.data;
  },

  /**
   * Export exam summary as JSON
   */
  exportJSON: async (examId) => {
    const response = await apiClient.get(`/api/export/${examId}/summary`);
    return response.data;
  },
};

export default examsAPI;
