import apiClient from './client'

/**
 * Submissions API endpoints - For uploading exam PDFs
 */
export const submissionsAPI = {
  /**
   * Upload a single submission/exam PDF
   */
  uploadSubmission: async (examId, file, studentName = null, rollNumber = null) => {
    const formData = new FormData()
    formData.append('exam_id', examId)
    formData.append('file', file)
    if (studentName) formData.append('student_name', studentName)
    if (rollNumber) formData.append('roll_number', rollNumber)

    const response = await apiClient.post('/api/submissions', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  /**
   * List submissions for an exam
   */
  listSubmissions: async (examId, limit = 20, offset = 0) => {
    const response = await apiClient.get('/api/submissions', {
      params: { exam_id: examId, limit, offset },
    })
    return response.data
  },

  /**
   * Get submission by ID
   */
  getSubmission: async (submissionId) => {
    const response = await apiClient.get(`/api/submissions/${submissionId}`)
    return response.data
  },

  /**
   * Delete submission
   */
  deleteSubmission: async (submissionId) => {
    const response = await apiClient.delete(`/api/submissions/${submissionId}`)
    return response.data
  },
}

export default submissionsAPI
