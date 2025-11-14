/**
 * Authentication Type Definitions
 *
 * Defines all authentication-related types including credentials,
 * responses, and authentication state. These types form the contract
 * between the frontend and backend authentication API.
 */

import { User } from './user.types';

/**
 * Login credentials required for user authentication
 */
export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

/**
 * Signup credentials for new user registration
 */
export interface SignupCredentials {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

/**
 * Standard authentication response from the API
 * Contains the JWT token and user information
 */
export interface AuthResponse {
  token: string;
  user: User;
  expiresIn?: number; // Token expiration in seconds
}

/**
 * Authentication state managed by AuthContext
 */
export interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
  token: string | null;
  error: string | null;
}

/**
 * Password reset request
 */
export interface PasswordResetRequest {
  email: string;
}

/**
 * Password reset confirmation
 */
export interface PasswordResetConfirm {
  token: string;
  newPassword: string;
  confirmPassword: string;
}

/**
 * Token validation response
 */
export interface TokenValidationResponse {
  valid: boolean;
  user?: User;
}
