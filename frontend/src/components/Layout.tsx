/**
 * Layout Component for X University Frontend
 * 
 * Provides the main application layout structure including navigation,
 * header, footer, and content area for all pages.
 * 
 * Features:
 * - Responsive navigation bar with authentication state
 * - Dynamic navigation based on user authentication status
 * - Consistent header and footer across all pages
 * - Active route highlighting in navigation
 * - User greeting and logout functionality
 * - Nested routing support with React Router Outlet
 * 
 * Layout Structure:
 * - Header: Logo, navigation links, user actions
 * - Main: Page content rendered via React Router
 * - Footer: Copyright and application information
 * 
 * Navigation:
 * - Home: Always visible to all users
 * - Monitor: System monitoring page for all users
 * - API Doc: Link to backend API documentation (external)
 * - Dashboard: Only visible when authenticated
 * - Login: Only visible when not authenticated
 * - Logout: Only visible when authenticated
 * 
 * @author X University Development Team
 * @created 2025
 */

import { Link, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../lib/auth'

/**
 * Main Layout Component
 * 
 * Renders the application layout with navigation, content area, and footer.
 * Handles authentication state and provides appropriate navigation options.
 */
export default function Layout() {
  const location = useLocation()
  const { user, isAuthenticated, logout } = useAuth()
  
  // Check if current route is dashboard page
  const isDashboard = location.pathname === '/dashboard'

  /**
   * Handle user logout
   * Calls the logout function from auth context and handles any errors gracefully.
   */
  const handleLogout = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('Logout failed:', error)
      // Continue with local logout even if server call fails
    }
  }

  // Don't show the layout header/footer on dashboard page
  if (isDashboard) {
    return <Outlet />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <div className="flex items-center">
                <svg className="h-8 w-8 text-blue-600 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                <h1 className="text-2xl font-bold text-gray-900">X University</h1>
              </div>
            </div>
            <nav className="flex items-center space-x-4">
              <Link
                to="/"
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  location.pathname === '/' 
                    ? 'text-blue-600 bg-blue-50' 
                    : 'text-gray-700 hover:text-gray-900'
                }`}
              >
                Home
              </Link>
              
              <Link
                to="/monitor"
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  location.pathname === '/monitor' 
                    ? 'text-green-600 bg-green-50' 
                    : 'text-gray-700 hover:text-gray-900'
                }`}
              >
                Monitor
              </Link>
              
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-2 rounded-md text-sm font-medium transition-colors text-gray-700 hover:text-gray-900 hover:bg-gray-50"
              >
                API Doc
              </a>
              
              {isAuthenticated ? (
                <>
                  <Link
                    to="/dashboard"
                    className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                  >
                    Dashboard
                  </Link>
                  <div className="flex items-center space-x-3">
                    <span className="text-sm text-gray-600">
                      Welcome, {user?.full_name?.split(' ')[0]}!
                    </span>
                    <button
                      onClick={handleLogout}
                      className="bg-red-600 text-white hover:bg-red-700 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                    >
                      Logout
                    </button>
                  </div>
                </>
              ) : (
                <Link
                  to="/login"
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    location.pathname === '/login' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  Login
                </Link>
              )}
            </nav>
          </div>
        </div>
      </header>

      <main>
        <Outlet />
      </main>

      <footer className="bg-white border-t">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-2">
              © 2025 X University. All rights reserved.
            </p>
            <p className="text-xs text-gray-500">
              Demo application showcasing modern authentication and dashboard design.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
