import React, { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'sonner'
import './App.css'

// Error Boundary
import ErrorBoundary from './components/ErrorBoundary'

// Hooks
import useDarkMode from './hooks/useDarkMode'
import { useAuthStore } from './store/authStore'

// Route Guards
import { ProtectedRoute, InstructorRoute, TARoute } from './components/RouteGuard'

// Pages
import Login from './pages/Login'
import InstructorDashboard from './pages/Dashboard'
import ExamUpload from './pages/ExamUpload'
import RubricSetup from './pages/RubricSetup'
import GradeExport from './pages/GradeExport'
import ReviewQueue from './pages/ReviewQueue'
import Unauthorized from './pages/Unauthorized'

function AppContent() {
  const { isDark } = useDarkMode()
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const role = useAuthStore((state) => state.role)

  return (
    <>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/unauthorized" element={<Unauthorized />} />

        {/* Instructor Routes */}
        <Route
          path="/dashboard"
          element={
            <InstructorRoute>
              <InstructorDashboard />
            </InstructorRoute>
          }
        />
        <Route
          path="/upload"
          element={
            <InstructorRoute>
              <ExamUpload />
            </InstructorRoute>
          }
        />
        <Route
          path="/upload/:examId"
          element={
            <InstructorRoute>
              <ExamUpload />
            </InstructorRoute>
          }
        />
        <Route
          path="/rubric/:examId"
          element={
            <InstructorRoute>
              <RubricSetup />
            </InstructorRoute>
          }
        />
        <Route
          path="/export/:examId"
          element={
            <InstructorRoute>
              <GradeExport />
            </InstructorRoute>
          }
        />
        {/* Also allow /export without examId param */}
        <Route
          path="/export"
          element={
            <InstructorRoute>
              <GradeExport />
            </InstructorRoute>
          }
        />

        {/* TA Routes */}
        <Route
          path="/review"
          element={
            <TARoute>
              <ReviewQueue />
            </TARoute>
          }
        />

        {/* Default route - redirect based on auth state */}
        <Route
          path="/"
          element={
            isAuthenticated
              ? role === 'instructor'
                ? <Navigate to="/dashboard" replace />
                : <Navigate to="/review" replace />
              : <Navigate to="/login" replace />
          }
        />

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      {/* Toast notifications */}
      <Toaster
        position="top-right"
        theme="dark"
        richColors
      />
    </>
  )
}

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
