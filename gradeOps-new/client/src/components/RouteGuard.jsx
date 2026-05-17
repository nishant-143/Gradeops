import { useAuthStore } from '../store/authStore';
import { Navigate } from 'react-router-dom';

/**
 * ProtectedRoute - Redirects to login if not authenticated
 */
export const ProtectedRoute = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

/**
 * InstructorRoute - Only accessible by instructors
 */
export const InstructorRoute = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const role = useAuthStore((state) => state.role);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (role !== 'instructor') {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

/**
 * TARoute - Only accessible by TAs
 */
export const TARoute = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const role = useAuthStore((state) => state.role);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (role !== 'ta') {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

export default { ProtectedRoute, InstructorRoute, TARoute };
