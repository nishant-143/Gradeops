import { create } from 'zustand';

/**
 * Exam Store - Manages exam data, list, and current exam context
 */
export const useExamStore = create((set, get) => ({
  // State
  exams: [],
  currentExam: null,
  examsLoading: false,
  examsError: null,
  totalExams: 0,
  currentPage: 1,
  pageSize: 20,

  // Actions
  setExams: (exams, total = exams.length) => {
    set({ exams, totalExams: total, examsError: null });
  },

  setCurrentExam: (exam) => {
    set({ currentExam: exam });
  },

  addExam: (exam) => {
    set((state) => ({
      exams: [exam, ...state.exams],
      totalExams: state.totalExams + 1,
    }));
  },

  updateExam: (examId, updates) => {
    set((state) => ({
      exams: state.exams.map((e) => (e.id === examId ? { ...e, ...updates } : e)),
      currentExam: state.currentExam?.id === examId 
        ? { ...state.currentExam, ...updates }
        : state.currentExam,
    }));
  },

  deleteExam: (examId) => {
    set((state) => ({
      exams: state.exams.filter((e) => e.id !== examId),
      totalExams: state.totalExams - 1,
      currentExam: state.currentExam?.id === examId ? null : state.currentExam,
    }));
  },

  setExamsLoading: (loading) => set({ examsLoading: loading }),
  setExamsError: (error) => set({ examsError: error }),
  setCurrentPage: (page) => set({ currentPage: page }),

  // Getters
  getExamById: (examId) => get().exams.find((e) => e.id === examId),
}));

