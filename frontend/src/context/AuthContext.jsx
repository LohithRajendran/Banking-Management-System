// context/AuthContext.jsx — Authentication State Management
// ============================================================
// React Context lets you share data across ALL components
// without passing it through props every time.
//
// This AuthContext stores:
//   - The current user (name, email, web_id)
//   - Whether the user is logged in
//   - Login / Logout / Signup functions
//
// HOW TO USE IN ANY COMPONENT:
//   import { useAuth } from '../context/AuthContext'
//   const { user, isLoggedIn, login, logout } = useAuth()

import { createContext, useContext, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/axios'
import toast from 'react-hot-toast'

// Step 1: Create the context
const AuthContext = createContext(null)


// Step 2: Create the Provider component
// Wrap your entire app with this so every component can access auth state
export function AuthProvider({ children }) {
  // State: current user object (null if not logged in)
  const [user, setUser] = useState(null)

  // State: whether the app is still loading (checking localStorage)
  const [loading, setLoading] = useState(true)

  const navigate = useNavigate()

  // ============================================
  // CHECK IF USER IS ALREADY LOGGED IN
  // ============================================
  // When the app first loads, check if there's a saved token in localStorage.
  // If yes, restore the user session.
  useEffect(() => {
    const savedUser = localStorage.getItem('user')
    const accessToken = localStorage.getItem('access_token')

    if (savedUser && accessToken) {
      try {
        setUser(JSON.parse(savedUser))
      } catch {
        // Corrupted data — clear it
        localStorage.clear()
      }
    }

    setLoading(false)  // Done checking
  }, [])


  // ============================================
  // SIGNUP FUNCTION
  // ============================================
  const signup = async (formData) => {
    try {
      const response = await api.post('/signup/', formData)
      const { user: userData, access, refresh } = response.data.data

      // Save tokens and user data
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      localStorage.setItem('user', JSON.stringify(userData))

      setUser(userData)
      toast.success(response.data.message)
      navigate('/create-account')

      return { success: true }
    } catch (error) {
      const errors = error.response?.data?.errors || {}
      const message = error.response?.data?.message || 'Signup failed. Please try again.'
      toast.error(message)
      return { success: false, errors }
    }
  }


  // ============================================
  // LOGIN FUNCTION
  // ============================================
  const login = async (email, password) => {
    try {
      const response = await api.post('/login/', { email, password })
      const { user: userData, access, refresh, has_bank_account } = response.data.data

      // Save tokens and user data
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      localStorage.setItem('user', JSON.stringify(userData))

      setUser(userData)
      toast.success(response.data.message)

      // Redirect based on whether they have a bank account
      if (has_bank_account) {
        navigate('/dashboard')
      } else {
        navigate('/create-account')
      }

      return { success: true }
    } catch (error) {
      const message = error.response?.data?.message || 'Login failed. Check your email and password.'
      toast.error(message)
      return { success: false }
    }
  }


  // ============================================
  // GOOGLE LOGIN / SIGNUP FUNCTION
  // ============================================
  // Called with the Google ID token (credential) after the user picks
  // an account in the Google popup. The backend verifies it, then either
  // logs the matching user in or creates a brand-new account for them.
  const googleLogin = async (credential) => {
    try {
      const response = await api.post('/auth/google/', { credential })
      const { user: userData, access, refresh, has_bank_account } = response.data.data

      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      localStorage.setItem('user', JSON.stringify(userData))

      setUser(userData)
      toast.success(response.data.message)

      if (has_bank_account) {
        navigate('/dashboard')
      } else {
        navigate('/create-account')
      }

      return { success: true }
    } catch (error) {
      const message = error.response?.data?.message || 'Google sign-in failed. Please try again.'
      toast.error(message)
      return { success: false }
    }
  }


  // ============================================
  // LOGOUT FUNCTION
  // ============================================
  const logout = () => {
    // Clear all saved data
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')

    setUser(null)
    navigate('/login')
    toast.success('You have been logged out.')
  }


  // ============================================
  // UPDATE USER in state (after account creation)
  // ============================================
  const updateUser = (updatedUser) => {
    setUser(updatedUser)
    localStorage.setItem('user', JSON.stringify(updatedUser))
  }


  // The value object is what components will receive when they call useAuth()
  const value = {
    user,
    isLoggedIn: !!user,
    loading,
    login,
    logout,
    signup,
    googleLogin,
    updateUser,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}


// Step 3: Custom hook for easy access
// Instead of: const { user } = useContext(AuthContext)
// You can write: const { user } = useAuth()
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used inside an AuthProvider')
  }
  return context
}
