// components/ProtectedRoute.jsx
// ================================
// A "guard" component that checks if the user is logged in.
//
// HOW IT WORKS:
//   - If user IS logged in → show the page (children)
//   - If user is NOT logged in → redirect to /login
//
// We wrap protected pages like this in App.jsx:
//   <ProtectedRoute>
//     <Dashboard />
//   </ProtectedRoute>

import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function ProtectedRoute({ children }) {
  const { isLoggedIn, loading } = useAuth()

  // While checking localStorage for saved token, show nothing
  if (loading) {
    return (
      <div className="page-loading">
        <div className="spinner spinner-light" style={{ width: 40, height: 40 }}></div>
        <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>Loading SecureBank...</p>
      </div>
    )
  }

  // Not logged in → redirect to login page
  if (!isLoggedIn) {
    return <Navigate to="/login" replace />
  }

  // Logged in → show the protected page
  return children
}

export default ProtectedRoute
