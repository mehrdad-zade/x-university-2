/**
 * Main Application Component for X University Frontend
 * 
 * This is the root component that sets up the application structure,
 * including routing, authentication context, and page layout.
 * 
 * Architecture:
 * - React Router for client-side navigation
 * - AuthProvider for global authentication state
 * - Route protection with ProtectedRoute and PublicRoute components
 * - Nested routing with Layout component
 * 
 * Routes:
 * - / (Home) - Public landing page
 * - /login - Public login page (redirects if authenticated)
 * - /dashboard - Protected dashboard page (requires authentication)
 * 
 * Features:
 * - Automatic authentication state management
 * - Route-based access control
 * - Responsive layout across all pages
 * - Loading states during authentication
 * 
 * @author X University Development Team
 * @created 2025
 */

import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './lib/auth'
import { ProtectedRoute, PublicRoute } from './components/ProtectedRoute'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import TermsPage from './pages/TermsPage'
import PrivacyPage from './pages/PrivacyPage'
import DashboardPage from './pages/DashboardPage'
import MonitorPage from './pages/MonitorPage'

/**
 * App Component
 * 
 * Root component that provides authentication context and routing structure.
 * All routes are wrapped with authentication logic and protected accordingly.
 */
function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Layout />}>
          {/* Public home page - accessible to all users */}
          <Route index element={<HomePage />} />
          
          {/* Public monitor page - accessible to all users */}
          <Route path="/monitor" element={<MonitorPage />} />
          
          {/* Public login page - only accessible when not authenticated */}
          <Route path="/login" element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          } />
          
          {/* Public register page - only accessible when not authenticated */}
          <Route path="/register" element={
            <PublicRoute>
              <RegisterPage />
            </PublicRoute>
          } />
          
          {/* Legal pages - accessible to all */}
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          
          {/* Protected dashboard - only accessible when authenticated */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          } />
        </Route>
      </Routes>
    </AuthProvider>
  )
}

export default App
