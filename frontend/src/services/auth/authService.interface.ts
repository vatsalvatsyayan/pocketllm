/**
 * Authentication Service Interface
 *
 * Defines the contract for authentication services.
 * This interface allows us to swap between mock and real implementations
 * without changing any component code (Dependency Inversion Principle).
 *
 * To switch from mock to real API:
 * 1. Implement this interface in a new class (e.g., ApiAuthService)
 * 2. Update the export in services/auth/index.ts
 * 3. No changes needed in components!
 */

import {
  LoginCredentials,
  SignupCredentials,
  AuthResponse,
  TokenValidationResponse,
} from '../../types/auth.types';

/**
 * Authentication service interface
 * All auth implementations must conform to this contract
 */
export interface IAuthService {
  /**
   * Authenticates user with email and password
   * @param credentials - User login credentials
   * @returns Promise with auth token and user data
   * @throws ApiError on authentication failure
   */
  login(credentials: LoginCredentials): Promise<AuthResponse>;

  /**
   * Registers a new user account
   * @param credentials - User signup credentials
   * @returns Promise with auth token and user data
   * @throws ApiError if registration fails or email exists
   */
  signup(credentials: SignupCredentials): Promise<AuthResponse>;

  /**
   * Logs out the current user
   * @returns Promise that resolves when logout is complete
   */
  logout(): Promise<void>;

  /**
   * Validates the current authentication token
   * @param token - JWT token to validate
   * @returns Promise with validation result and user data if valid
   */
  validateToken(token: string): Promise<TokenValidationResponse>;

  /**
   * Refreshes the authentication token
   * @param refreshToken - Refresh token
   * @returns Promise with new auth token
   */
  refreshToken(refreshToken: string): Promise<AuthResponse>;
}
