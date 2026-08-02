// App.jsx — The Root Component
// ================================
// This is the "skeleton" of the entire React app.
// It sets up:
//   1. React Router — which page to show based on the URL
//   2. AuthProvider — authentication state for the whole app
//   3. Toast notifications — popup messages (success/error)
//
// ROUTING EXPLAINED:
//   /login        → Login page
//   /signup       → Signup page
//   /create-account → Create bank account page
//   /dashboard    → Main dashboard (protected — must be logged in)
//   /transfer     → Transfer money (protected)
//   /history      → Transaction history (protected)
//   /             → Redirects to /dashboard or /login

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'

// Pages
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import Transfer from './pages/Transfer'
import History from './pages/History'
import CreateAccount from './pages/CreateAccount'

function App() {
  return (
    // BrowserRouter enables navigation between pages without full page reloads
    <BrowserRouter>
      {/* AuthProvider wraps everything so all pages can access user state */}
      <AuthProvider>

        {/* Toast Notifications — the popup messages at the top of the screen */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#0d1829',
              color: '#f1f5f9',
              border: '1px solid rgba(245, 158, 11, 0.2)',
              borderRadius: '12px',
              fontFamily: 'Inter, sans-serif',
              fontSize: '14px',
            },
            success: {
              iconTheme: { primary: '#f59e0b', secondary: '#000' },
            },
            error: {
              iconTheme: { primary: '#ef4444', secondary: '#fff' },
            },
          }}
        />

        {/* Define all the routes (pages) of the app */}
        <Routes>
          {/* Public routes — anyone can visit */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* Protected routes — must be logged in */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/transfer"
            element={
              <ProtectedRoute>
                <Transfer />
              </ProtectedRoute>
            }
          />
          <Route
            path="/history"
            element={
              <ProtectedRoute>
                <History />
              </ProtectedRoute>
            }
          />
          <Route
            path="/create-account"
            element={
              <ProtectedRoute>
                <CreateAccount />
              </ProtectedRoute>
            }
          />

          {/* Default: redirect / to /dashboard */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />

          {/* 404: redirect unknown URLs to dashboard */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>

      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
