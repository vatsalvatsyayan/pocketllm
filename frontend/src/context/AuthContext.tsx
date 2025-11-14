/**
 * Authentication Context
 *
 * Provides global authentication state and functions to the entire app.
 * Uses React Context API for state management.
 *
 * Features:
 * - Centralized auth state
 * - Automatic token validation on mount
 * - Session persistence
 * - Login/logout/signup functions
 */

import React, { createContext, useState, useEffect, useCallback } from 'react';
import { LoginCredentials, SignupCredentials, AuthState } from '../types/auth.types';
import { authService } from '../services/auth';
import {
  getToken,
  getUser,
  setToken,
  setUser,
  clearAuthData,
  hasValidSession,
} from '../services/storage/tokenStorage';
import { handleApiError, logError } from '../utils/errorHandler';

/**
 * Auth context value interface
 */
interface AuthContextValue extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  signup: (credentials: SignupCredentials) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

/**
 * Create Auth Context
 */
export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/**
 * Auth Provider Props
 */
interface AuthProviderProps {
  children: React.ReactNode;
}

/**
 * Auth Provider Component
 * Wraps the app and provides authentication state
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    user: null,
    token: null,
    error: null,
  });

  /**
   * Initialize auth state from storage
   */
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Check if user has a valid session
        if (hasValidSession()) {
          const token = getToken();
          const user = getUser();

          if (token && user) {
            // Validate token with backend (in mock, this just checks if token is valid)
            const validation = await authService.validateToken(token);

            if (validation.valid && validation.user) {
              setState({
                isAuthenticated: true,
                isLoading: false,
                user: validation.user,
                token,
                error: null,
              });
              return;
            }
          }
        }

        // No valid session
        clearAuthData();
        setState({
          isAuthenticated: false,
          isLoading: false,
          user: null,
          token: null,
          error: null,
        });
      } catch (error) {
        logError(error, 'Auth initialization');
        clearAuthData();
        setState({
          isAuthenticated: false,
          isLoading: false,
          user: null,
          token: null,
          error: null,
        });
      }
    };

    initializeAuth();
  }, []);

  /**
   * Login function
   */
  const login = useCallback(async (credentials: LoginCredentials) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await authService.login(credentials);

      // Store token and user
      setToken(response.token, response.expiresIn);
      setUser(response.user);

      setState({
        isAuthenticated: true,
        isLoading: false,
        user: response.user,
        token: response.token,
        error: null,
      });
    } catch (error) {
      const errorMessage = handleApiError(error);
      logError(error, 'Login');

      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));

      throw error;
    }
  }, []);

  /**
   * Signup function
   */
  const signup = useCallback(async (credentials: SignupCredentials) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await authService.signup(credentials);

      // Store token and user
      setToken(response.token, response.expiresIn);
      setUser(response.user);

      setState({
        isAuthenticated: true,
        isLoading: false,
        user: response.user,
        token: response.token,
        error: null,
      });
    } catch (error) {
      const errorMessage = handleApiError(error);
      logError(error, 'Signup');

      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));

      throw error;
    }
  }, []);

  /**
   * Logout function
   */
  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } catch (error) {
      logError(error, 'Logout');
    } finally {
      // Always clear local state and storage
      clearAuthData();
      setState({
        isAuthenticated: false,
        isLoading: false,
        user: null,
        token: null,
        error: null,
      });
    }
  }, []);

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  const value: AuthContextValue = {
    ...state,
    login,
    signup,
    logout,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
