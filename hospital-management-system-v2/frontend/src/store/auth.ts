import { defineStore } from 'pinia'
import axios from 'axios'

interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: string
  department: string
}

interface AuthState {
  isAuthenticated: boolean
  user: User | null
  token: string | null
  loading: boolean
  error: string | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    isAuthenticated: false,
    user: null,
    token: null,
    loading: false,
    error: null
  }),

  getters: {
    isAdmin: (state) => state.user?.role === 'admin',
    currentUser: (state) => state.user
  },

  actions: {
    async login(username: string, password: string) {
      this.loading = true
      this.error = null
      
      try {
        // Mock API call - in real app, this would be an actual API request
        // const response = await axios.post('/api/auth/login', { username, password })
        // const { user, token } = response.data
        
        // Mock data for demonstration
        const mockUser: User = {
          id: 1,
          username: username,
          email: `${username}@hospital.com`,
          full_name: 'Dr. John Doe',
          role: 'doctor',
          department: 'Cardiology'
        }
        const mockToken = 'mock-jwt-token'
        
        localStorage.setItem('token', mockToken)
        localStorage.setItem('user', JSON.stringify(mockUser))
        
        this.isAuthenticated = true
        this.user = mockUser
        this.token = mockToken
        
        return true
      } catch (error: any) {
        this.error = error.message || 'Login failed'
        return false
      } finally {
        this.loading = false
      }
    },

    async register(userData: any) {
      this.loading = true
      this.error = null
      
      try {
        // Mock API call
        // const response = await axios.post('/api/auth/register', userData)
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        return true
      } catch (error: any) {
        this.error = error.message || 'Registration failed'
        return false
      } finally {
        this.loading = false
      }
    },

    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.isAuthenticated = false
      this.user = null
      this.token = null
    },

    checkAuth() {
      const token = localStorage.getItem('token')
      const userStr = localStorage.getItem('user')
      
      if (token && userStr) {
        this.isAuthenticated = true
        this.token = token
        this.user = JSON.parse(userStr)
      }
    }
  }
})