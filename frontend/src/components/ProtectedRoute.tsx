/**
 * Route Protection Components for X University Frontend
 * 
 * Provides authentication-based route protection using React Router and
 * the authentication context. Includes components for both protected and
 * public-only routes.
 * 
 * Components:
 * - ProtectedRoute: Requires authentication, redirects to login if not authenticated
 * - PublicRoute: Only accessible when not authenticated, redirects to dashboard if authenticated
 * 
 * Features:
 * - Automatic redirection based on authentication state
 * - Loading states while authentication is being determined
 * - Preserve navigation state for post-login redirects
 * - Consistent loading UI across route transitions
 * 
 * Usage:
 *   <ProtectedRoute>
 *     <DashboardPage />
 *   </ProtectedRoute>
 * 
 *   <PublicRoute>
 *     <LoginPage />
 *   </PublicRoute>
 * 
 * @author X University Development Team
 * @created 2025
 */

import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../lib/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function ProtectedRoute({ children, fallback }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      fallback || (
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      )
    );
  }

  if (!isAuthenticated) {
    // Redirect to login page with return url
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}

/**
 * Public Route Component
 * 
 * Protects routes that should only be accessible when NOT authenticated
 * (like login page). If user is authenticated, redirects to dashboard.
 * 
 * @param children - Components to render when not authenticated
 */
export function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading state while authentication is being determined
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect authenticated users to dashboard
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  // User is not authenticated, render the public content
  return <>{children}</>;
}
