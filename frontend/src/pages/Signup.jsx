// pages/Signup.jsx — Signup / Registration Page
// ================================================
// New users fill this form to create an account.
// After signup, they are automatically logged in
// and redirected to create their bank account.

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { GoogleLogin } from '@react-oauth/google'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'
import { User, Mail, Lock, Eye, EyeOff, Shield, ArrowRight, CheckCircle } from 'lucide-react'

function Signup() {
  const { signup, googleLogin } = useAuth()

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    confirm_password: '',
  })

  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState({})

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: '' }))
  }

  // Password strength checker
  const getPasswordStrength = (password) => {
    if (!password) return null
    let score = 0
    if (password.length >= 8) score++
    if (/[A-Z]/.test(password)) score++
    if (/[0-9]/.test(password)) score++
    if (/[^A-Za-z0-9]/.test(password)) score++
    if (score <= 1) return { label: 'Weak', color: 'var(--red)', width: '25%' }
    if (score === 2) return { label: 'Fair', color: '#f59e0b', width: '50%' }
    if (score === 3) return { label: 'Good', color: '#10b981', width: '75%' }
    return { label: 'Strong', color: '#10b981', width: '100%' }
  }

  const strength = getPasswordStrength(formData.password)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrors({})

    // Validation
    const newErrors = {}
    if (!formData.first_name.trim()) newErrors.first_name = 'First name is required'
    if (!formData.last_name.trim()) newErrors.last_name = 'Last name is required'
    if (!formData.email) newErrors.email = 'Email is required'
    if (!formData.password) newErrors.password = 'Password is required'
    if (formData.password.length < 8) newErrors.password = 'Password must be at least 8 characters'
    if (formData.password !== formData.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match'
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    setIsLoading(true)
    const result = await signup(formData)
    if (!result.success && result.errors) {
      setErrors(result.errors)
    }
    setIsLoading(false)
  }

  return (
    <div className="auth-page">
      <div className="auth-card" style={{ maxWidth: 520 }}>

        {/* Logo */}
        <div className="auth-logo">
          <div className="auth-logo-icon">
            <Shield size={26} color="#000" strokeWidth={2.5} />
          </div>
          <div className="auth-logo-text">Secure<span>Bank</span></div>
        </div>

        <h1 className="auth-title">Create your account</h1>
        <p className="auth-subtitle">Join SecureBank — free, fast, and secure</p>

        <form onSubmit={handleSubmit} noValidate>

          {/* Name Row */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label className="form-label" htmlFor="first_name">First Name</label>
              <div className="input-with-icon">
                <User size={16} className="input-icon" />
                <input
                  id="first_name"
                  name="first_name"
                  type="text"
                  className={`form-input ${errors.first_name ? 'error' : ''}`}
                  placeholder="John"
                  value={formData.first_name}
                  onChange={handleChange}
                  autoFocus
                />
              </div>
              {errors.first_name && <p className="form-error">{errors.first_name}</p>}
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="last_name">Last Name</label>
              <input
                id="last_name"
                name="last_name"
                type="text"
                className={`form-input ${errors.last_name ? 'error' : ''}`}
                placeholder="Doe"
                value={formData.last_name}
                onChange={handleChange}
              />
              {errors.last_name && <p className="form-error">{errors.last_name}</p>}
            </div>
          </div>

          {/* Email */}
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
              />
            </div>
            {errors.email && <p className="form-error">{errors.email}</p>}
          </div>

          {/* Password */}
          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <div className="input-with-icon">
              <Lock size={16} className="input-icon" />
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                className={`form-input ${errors.password ? 'error' : ''}`}
                placeholder="Min. 8 characters"
                value={formData.password}
                onChange={handleChange}
                style={{ paddingRight: 44 }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(s => !s)}
                style={{
                  position: 'absolute', right: 14, top: '50%',
                  transform: 'translateY(-50%)', background: 'none',
                  border: 'none', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex',
                }}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {errors.password && <p className="form-error">{errors.password}</p>}

            {/* Password Strength Bar */}
            {formData.password && strength && (
              <div style={{ marginTop: 8 }}>
                <div style={{
                  height: 4, background: 'var(--border-subtle)',
                  borderRadius: 999, overflow: 'hidden',
                }}>
                  <div style={{
                    height: '100%', width: strength.width,
                    background: strength.color,
                    borderRadius: 999,
                    transition: 'width 0.3s ease',
                  }} />
                </div>
                <p style={{ fontSize: 11, color: strength.color, marginTop: 4 }}>
                  Password strength: {strength.label}
                </p>
              </div>
            )}
          </div>

          {/* Confirm Password */}
          <div className="form-group">
            <label className="form-label" htmlFor="confirm_password">Confirm Password</label>
            <div className="input-with-icon">
              <Lock size={16} className="input-icon" />
              <input
                id="confirm_password"
                name="confirm_password"
                type={showConfirm ? 'text' : 'password'}
                className={`form-input ${errors.confirm_password ? 'error' : ''}`}
                placeholder="Repeat your password"
                value={formData.confirm_password}
                onChange={handleChange}
                style={{ paddingRight: 44 }}
              />
              <button
                type="button"
                onClick={() => setShowConfirm(s => !s)}
                style={{
                  position: 'absolute', right: 14, top: '50%',
                  transform: 'translateY(-50%)', background: 'none',
                  border: 'none', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex',
                }}
              >
                {showConfirm ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {errors.confirm_password && <p className="form-error">{errors.confirm_password}</p>}
            {/* Match indicator */}
            {formData.confirm_password && formData.password === formData.confirm_password && (
              <p style={{ fontSize: 12, color: 'var(--green)', marginTop: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
                <CheckCircle size={12} /> Passwords match
              </p>
            )}
          </div>

          {/* Submit */}
          <button
            type="submit"
            className="btn btn-primary btn-full btn-lg"
            disabled={isLoading}
          >
            {isLoading ? (
              <><span className="spinner"></span> Creating account...</>
            ) : (
              <>Create Account <ArrowRight size={18} /></>
            )}
          </button>
        </form>

        {/* Divider */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '24px 0' }}>
          <hr className="auth-divider" style={{ flex: 1, margin: 0 }} />
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>OR</span>
          <hr className="auth-divider" style={{ flex: 1, margin: 0 }} />
        </div>

        {/* Google Sign-Up */}
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <GoogleLogin
            onSuccess={(credentialResponse) => googleLogin(credentialResponse.credential)}
            onError={() => toast.error('Google sign-up failed. Please try again.')}
            text="signup_with"
            width="320"
          />
        </div>

        <p className="auth-footer" style={{ marginTop: 24 }}>
          Already have an account? <Link to="/login">Sign in</Link>
        </p>

      </div>
    </div>
  )
}

export default Signup
