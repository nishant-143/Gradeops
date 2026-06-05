import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * Auth Store - Manages user session, JWT token, and role
 * Persisted in localStorage
 */
export const useAuthStore = create(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: null,
      role: null, // 'instructor' or 'ta'
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      setUser: (user, token) => {
        set({
          user,
          token,
          role: user?.role || null,
          isAuthenticated: !!token,
          error: null,
        });
      },

      logout: () => {
        set({
          user: null,
          token: null,
          role: null,
          isAuthenticated: false,
          error: null,
        });
      },

      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),

      // Getters
      isInstructor: () => get().role === 'instructor',
      isTA: () => get().role === 'ta',
    }),
    {
      name: 'gradeops-auth', // localStorage key
    }
  )
);
