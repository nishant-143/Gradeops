import { create } from 'zustand';

/**
 * Grade Store - Manages grades, grading queue, and approval workflow
 * Used primarily by TAs in the grading dashboard
 */
export const useGradeStore = create((set, get) => ({
  // State
  grades: [],
  gradeQueue: [],
  currentGrade: null,
  currentIndex: 0,
  gradesLoading: false,
  gradesError: null,
  totalGrades: 0,
  totalPending: 0,
  totalApproved: 0,
  totalOverridden: 0,

  // Actions
  setGrades: (grades, total = grades.length) => {
    set({
      grades,
      totalGrades: total,
      gradesError: null,
      totalPending: grades.filter((g) => g.ta_status === 'pending').length,
      totalApproved: grades.filter((g) => g.ta_status === 'approved').length,
      totalOverridden: grades.filter((g) => g.ta_status === 'overridden').length,
    });
  },

  setGradeQueue: (queue) => {
    set({
      gradeQueue: queue,
      currentGrade: queue.length > 0 ? queue[0] : null,
      currentIndex: 0,
    });
  },

  setCurrentGrade: (grade, index = 0) => {
    set({ currentGrade: grade, currentIndex: index });
  },

  nextGrade: () => {
    const { gradeQueue, currentIndex } = get();
    if (currentIndex < gradeQueue.length - 1) {
      const nextIndex = currentIndex + 1;
      set({
        currentGrade: gradeQueue[nextIndex],
        currentIndex: nextIndex,
      });
    }
  },

  previousGrade: () => {
    const { currentIndex } = get();
    if (currentIndex > 0) {
      const prevIndex = currentIndex - 1;
      const { gradeQueue } = get();
      set({
        currentGrade: gradeQueue[prevIndex],
        currentIndex: prevIndex,
      });
    }
  },

  updateGrade: (gradeId, updates) => {
    set((state) => ({
      grades: state.grades.map((g) => (g.id === gradeId ? { ...g, ...updates } : g)),
      gradeQueue: state.gradeQueue.map((g) => 
        g.id === gradeId ? { ...g, ...updates } : g
      ),
      currentGrade: state.currentGrade?.id === gradeId 
        ? { ...state.currentGrade, ...updates }
        : state.currentGrade,
    }));
  },

  removeFromQueue: (gradeId) => {
    set((state) => {
      const newQueue = state.gradeQueue.filter((g) => g.id !== gradeId);
      return {
        gradeQueue: newQueue,
        currentGrade: newQueue.length > state.currentIndex
          ? newQueue[state.currentIndex]
          : newQueue.length > 0
          ? newQueue[newQueue.length - 1]
          : null,
      };
    });
  },

  setGradesLoading: (loading) => set({ gradesLoading: loading }),
  setGradesError: (error) => set({ gradesError: error }),

  // Getters
  getGradeById: (gradeId) => get().grades.find((g) => g.id === gradeId),
  hasMoreGrades: () => get().currentIndex < get().gradeQueue.length - 1,
}));

