import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './lib/auth'
import { ProtectedRoute, PublicRoute } from './components/ProtectedRoute'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="/login" element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          } />
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
