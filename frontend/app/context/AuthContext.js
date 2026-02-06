/**
 * Authentication Context
 * ======================
 * Global state management for user authentication.
 * 
 * WHY: Share authentication state across all React components
 * WHERE: Wrap entire app in app/layout.js
 * HOW: React Context API with localStorage for token persistence
 * 
 * PROVIDES:
 *   - user: Current user object (or null if not logged in)
 *   - token: JWT access token
 *   - login(email, password): Login and store token
 *   - register(email, username, password): Create new account
 *   - logout(): Clear token and user data
 *   - isLoading: Whether auth state is being initialized
 *   - isAuthenticated: Boolean - is user logged in?
 *   - isAdmin: Boolean - does user have admin role?
 */

'use client';

import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext({});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // ============= INITIALIZE AUTH STATE ON MOUNT =============
  // WHY: Check if user was previously logged in
  // HOW: Load token from localStorage and fetch user info
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Check for stored token
        const storedToken = localStorage.getItem('token');
        
        if (storedToken) {
          setToken(storedToken);
          
          // Fetch user info with stored token
          const response = await fetch('http://localhost:8000/auth/me', {
            headers: {
              'Authorization': `Bearer ${storedToken}`
            }
          });
          
          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
          } else {
            // Token invalid - clear it
            localStorage.removeItem('token');
            setToken(null);
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        localStorage.removeItem('token');
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  /**
   * Login user with email and password
   * 
   * @param {string} email - User's email
   * @param {string} password - User's password
   * @returns {Promise<{success: boolean, error?: string}>}
   * 
   * FLOW:
   *   1. POST to /auth/login
   *   2. Receive JWT token
   *   3. Store token in localStorage
   *   4. Fetch user info with token
   *   5. Update state
   */
  const login = async (email, password) => {
    try {
      // Call login API
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        const error = await response.json();
        return { 
          success: false, 
          error: error.detail || 'Login failed' 
        };
      }

      const data = await response.json();
      const accessToken = data.access_token;

      // Store token
      localStorage.setItem('token', accessToken);
      setToken(accessToken);

      // Fetch user info
      const userResponse = await fetch('http://localhost:8000/auth/me', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });

      if (userResponse.ok) {
        const userData = await userResponse.json();
        setUser(userData);
        return { success: true };
      }

      return { success: false, error: 'Failed to fetch user info' };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Network error' };
    }
  };

  /**
   * Register new user account
   * 
   * @param {string} email - User's email
   * @param {string} username - User's username
   * @param {string} password - User's password
   * @returns {Promise<{success: boolean, error?: string}>}
   * 
   * FLOW:
   *   1. POST to /auth/register
   *   2. Account created with role='user'
   *   3. Auto-login after registration
   */
  const register = async (email, username, password) => {
    try {
      // Call register API
      const response = await fetch('http://localhost:8000/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, username, password })
      });

      if (!response.ok) {
        const error = await response.json();
        return { 
          success: false, 
          error: error.detail || 'Registration failed' 
        };
      }

      // Auto-login after successful registration
      return await login(email, password);
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'Network error' };
    }
  };

  /**
   * Logout current user
   * 
   * FLOW:
   *   1. Clear token from localStorage
   *   2. Clear user state
   *   3. Redirect to login page (handled by component)
   */
  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  /**
   * Refresh user data
   * Useful after profile updates
   */
  const refreshUser = async () => {
    if (!token) return;

    try {
      const response = await fetch('http://localhost:8000/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      }
    } catch (error) {
      console.error('Failed to refresh user:', error);
    }
  };

  // ============= COMPUTED VALUES =============
  const isAuthenticated = !!user && !!token;
  const isAdmin = user?.role === 'admin';

  // Context value provided to all children
  const value = {
    user,
    token,
    isLoading,
    isAuthenticated,
    isAdmin,
    login,
    register,
    logout,
    refreshUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to use auth context in components
 * 
 * USAGE:
 *   const { user, login, logout, isAuthenticated, isAdmin } = useAuth();
 *   
 *   if (!isAuthenticated) {
 *     return <LoginForm onSubmit={login} />;
 *   }
 *   
 *   if (isAdmin) {
 *     return <AdminPanel />;
 *   }
 */
export function useAuth() {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  
  return context;
}
