// pages/Login.jsx — Login Page
// ================================
// The login form. Users enter their email and password.
// On success: saves JWT tokens + redirects to dashboard.

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { GoogleLogin } from '@react-oauth/google'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'
import { Mail, Lock, Eye, EyeOff, Shield, ArrowRight } from 'lucide-react'

function Login() {
  const { login, googleLogin } = useAuth()

  // Form fields state
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })

  // UI states
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState({})

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    // Clear error for this field when user starts typing
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: '' }))
  }

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrors({})

    // Simple validation
    const newErrors = {}
    if (!formData.email) newErrors.email = 'Email is required'
    if (!formData.password) newErrors.password = 'Password is required'

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    setIsLoading(true)
    await login(formData.email, formData.password)
    setIsLoading(false)
  }

  return (
    <div className="auth-page">
      <div className="auth-card">

        {/* Logo */}
        <div className="auth-logo">
          <div className="auth-logo-icon">
            <Shield size={26} color="#000" strokeWidth={2.5} />
          </div>
          <div className="auth-logo-text">Secure<span>Bank</span></div>
        </div>

        {/* Header */}
        <h1 className="auth-title">Welcome back</h1>
        <p className="auth-subtitle">Sign in to your banking account</p>

        {/* Login Form */}
        <form onSubmit={handleSubmit} noValidate>

          {/* Email Field */}
          <div className="form-group">
            <label className="form-label" htmlFor="email">Email Address</label>
            <div className="input-with-icon">
              <Mail size={16} className="input-icon" />
              <input
                id="email"
                name="email"
                type="email"
                className={`form-input ${errors.email ? 'error' : ''}`}
                placeholder="john@example.com"
                value={formData.email}
                onChange={handleChange}
                autoComplete="email"
                autoFocus
              />
            </div>
            {errors.email && <p className="form-error">{errors.email}</p>}
          </div>

          {/* Password Field */}
          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <div className="input-with-icon">
              <Lock size={16} className="input-icon" />
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                className={`form-input ${errors.password ? 'error' : ''}`}
                placeholder="Enter your password"
                value={formData.password}
                onChange={handleChange}
                autoComplete="current-password"
                style={{ paddingRight: 44 }}
              />
              {/* Toggle password visibility */}
              <button
                type="button"
                onClick={() => setShowPassword(s => !s)}
                style={{
                  position: 'absolute',
                  right: 14,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  padding: 0,
                  display: 'flex',
                }}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {errors.password && <p className="form-error">{errors.password}</p>}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="btn btn-primary btn-full btn-lg"
            disabled={isLoading}
            style={{ marginTop: 8 }}
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                Signing in...
              </>
            ) : (
              <>
                Sign In
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        {/* Google Sign-In */}
        {import.meta.env.VITE_GOOGLE_CLIENT_ID && (
          <>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '24px 0' }}>
              <hr className="auth-divider" style={{ flex: 1, margin: 0 }} />
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>OR</span>
              <hr className="auth-divider" style={{ flex: 1, margin: 0 }} />
            </div>

            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <GoogleLogin
                onSuccess={(credentialResponse) => googleLogin(credentialResponse.credential)}
                onError={() => toast.error('Google sign-in failed. Please try again.')}
                text="signin_with"
                width="320"
              />
            </div>
          </>
        )}

        {/* Footer */}
        <p className="auth-footer" style={{ marginTop: 28 }}>
          Don't have an account?{' '}
          <Link to="/signup">Create one for free</Link>
        </p>

        {/* Demo hint */}
        <div className="alert alert-info" style={{ marginTop: 20, fontSize: 12 }}>
          <span>💡</span>
          <span>
            <strong>First time?</strong> Create an account, then create a bank account to get started with ₹1000 bonus!
          </span>
        </div>

      </div>
    </div>
  )
}

export default Login
