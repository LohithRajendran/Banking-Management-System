// components/Navbar.jsx — Navigation Bar
// =========================================
// The top bar shown on all protected pages (Dashboard, Transfer, History).
// Shows:
//   - SecureBank logo
//   - Navigation links (Dashboard, Transfer, History)
//   - User avatar + name + logout button

import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  LayoutDashboard,
  ArrowLeftRight,
  History,
  LogOut,
  Shield,
} from 'lucide-react'

function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  // Get user's initials for the avatar (e.g., "John Doe" → "JD")
  const getInitials = () => {
    if (!user) return '?'
    const first = user.first_name?.[0] || ''
    const last = user.last_name?.[0] || ''
    return (first + last).toUpperCase() || user.email?.[0]?.toUpperCase() || '?'
  }

  return (
    <nav className="navbar">
      <div className="container navbar-inner">

        {/* Logo */}
        <div
          className="navbar-brand"
          style={{ cursor: 'pointer' }}
          onClick={() => navigate('/dashboard')}
        >
          <div className="navbar-logo-icon">
            <Shield size={20} color="#000" strokeWidth={2.5} />
          </div>
          Secure<span>Bank</span>
        </div>

        {/* Navigation Links */}
        <div className="navbar-nav">
          <NavLink
            to="/dashboard"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <LayoutDashboard size={16} />
            Dashboard
          </NavLink>

          <NavLink
            to="/transfer"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <ArrowLeftRight size={16} />
            Transfer
          </NavLink>

          <NavLink
            to="/history"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <History size={16} />
            History
          </NavLink>
        </div>

        {/* User Info + Logout */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {/* User avatar pill */}
          <div className="navbar-user">
            <div className="navbar-avatar">{getInitials()}</div>
            <span style={{ fontSize: 13 }}>{user?.first_name} {user?.last_name}</span>
          </div>

          {/* Logout button */}
          <button
            onClick={logout}
            className="btn btn-ghost btn-sm"
            title="Logout"
            style={{ padding: '8px 12px' }}
          >
            <LogOut size={15} />
            <span style={{ fontSize: 13 }}>Logout</span>
          </button>
        </div>

      </div>
    </nav>
  )
}

export default Navbar
