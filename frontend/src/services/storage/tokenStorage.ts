/**
 * Token Storage Service
 *
 * Manages secure storage and retrieval of authentication tokens.
 * Uses localStorage for persistence (consider httpOnly cookies for production).
 */

import { AUTH_CONFIG } from '../../utils/constants';
import { User } from '../../types/user.types';

/**
 * Stores authentication token in localStorage
 */
export const setToken = (token: string, expiresIn?: number): void => {
  localStorage.setItem(AUTH_CONFIG.TOKEN_KEY, token);

  if (expiresIn) {
    const expiryTime = Date.now() + expiresIn * 1000;
    localStorage.setItem(AUTH_CONFIG.TOKEN_EXPIRY_KEY, expiryTime.toString());
  }
};

/**
 * Retrieves authentication token from localStorage
 */
export const getToken = (): string | null => {
  const token = localStorage.getItem(AUTH_CONFIG.TOKEN_KEY);

  if (!token) {
    return null;
  }

  // Check if token has expired
  const expiry = localStorage.getItem(AUTH_CONFIG.TOKEN_EXPIRY_KEY);
  if (expiry && Date.now() > parseInt(expiry, 10)) {
    clearToken();
    return null;
  }

  return token;
};

/**
 * Removes authentication token from localStorage
 */
export const clearToken = (): void => {
  localStorage.removeItem(AUTH_CONFIG.TOKEN_KEY);
  localStorage.removeItem(AUTH_CONFIG.TOKEN_EXPIRY_KEY);
};

/**
 * Stores user data in localStorage
 */
export const setUser = (user: User): void => {
  localStorage.setItem(AUTH_CONFIG.USER_KEY, JSON.stringify(user));
};

/**
 * Retrieves user data from localStorage
 */
export const getUser = (): User | null => {
  const userStr = localStorage.getItem(AUTH_CONFIG.USER_KEY);

  if (!userStr) {
    return null;
  }

  try {
    return JSON.parse(userStr);
  } catch (error) {
    console.error('Failed to parse user data:', error);
    return null;
  }
};

/**
 * Removes user data from localStorage
 */
export const clearUser = (): void => {
  localStorage.removeItem(AUTH_CONFIG.USER_KEY);
};

/**
 * Clears all authentication data
 */
export const clearAuthData = (): void => {
  clearToken();
  clearUser();
};

/**
 * Checks if user has a valid session
 */
export const hasValidSession = (): boolean => {
  return getToken() !== null && getUser() !== null;
};
