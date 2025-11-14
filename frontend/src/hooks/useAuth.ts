/**
 * useAuth Hook
 *
 * Custom hook to access authentication context.
 * Provides type-safe access to auth state and functions.
 *
 * Usage:
 * const { user, isAuthenticated, login, logout } = useAuth();
 */

import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

/**
 * Hook to access authentication context
 * @throws Error if used outside AuthProvider
 */
export const useAuth = () => {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
};
