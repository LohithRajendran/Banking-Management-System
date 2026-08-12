// api/axios.js — Configured Axios HTTP Client
// =============================================
// Axios is a library that makes HTTP requests easy.
// This file sets up ONE shared axios instance that:
//   1. Automatically sends to our Django backend (http://localhost:8000)
//   2. Automatically adds the JWT token to every request header
//   3. Automatically refreshes the token if it expires
//   4. Redirects to login if the session is invalid

import axios from 'axios'

// Base URL for all API calls
// In production: set VITE_API_URL in a .env file (e.g. VITE_API_URL=https://api.yourdomain.com/api)
// In development: Vite's proxy handles /api → localhost:8000, so we use a relative '/api'
let rawUrl = import.meta.env.VITE_API_URL || '/api'
if (rawUrl.startsWith('http') && !rawUrl.replace(/\/$/, '').endsWith('/api')) {
  rawUrl = rawUrl.replace(/\/$/, '') + '/api'
}
const BASE_URL = rawUrl

// Create the axios instance
const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ============================================
// REQUEST INTERCEPTOR
// ============================================
// This runs BEFORE every request is sent.
// It automatically adds the JWT token to the Authorization header.
//
// Example of what it adds:
//   Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
api.interceptors.request.use(
  (config) => {
    // Get the access token from localStorage
    const token = localStorage.getItem('access_token')

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => Promise.reject(error)
)


// ============================================
// RESPONSE INTERCEPTOR
// ============================================
// This runs AFTER every response is received.
// If we get a 401 (Unauthorized) error, it means our token expired.
// We try to get a new token using the refresh token.
// If the refresh also fails, we log the user out.
api.interceptors.response.use(
  // Success: just return the response
  (response) => response,

  // Error: try to refresh the token
  async (error) => {
    const originalRequest = error.config

    // Is this a 401 (Unauthorized) error that we haven't already retried?
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true  // Mark as retried to avoid infinite loop

      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        try {
          // Try to get a new access token
          const response = await axios.post(`${BASE_URL}/token/refresh/`, {
            refresh: refreshToken,
          })

          const newAccessToken = response.data.access

          // Save the new token
          localStorage.setItem('access_token', newAccessToken)

          // Retry the original request with the new token
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
          return api(originalRequest)

        } catch (refreshError) {
          // Refresh failed — log the user out
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      } else {
        // No refresh token — go to login
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api
