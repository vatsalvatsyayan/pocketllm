import { apiClient } from '../api/apiClient';
import { AUTH_ENDPOINTS } from '../api/endpoints';
import { IAuthService } from './authService.interface';
import {
  AuthResponse,
  LoginCredentials,
  SignupCredentials,
  TokenValidationResponse,
} from '../../types/auth.types';
import { createApiError } from '../../utils/errorHandler';

/**
 * API-backed authentication service that talks to the backend JWT endpoints.
 */
export class ApiAuthService implements IAuthService {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      return await apiClient.post<AuthResponse>(
        AUTH_ENDPOINTS.LOGIN,
        {
          email: credentials.email,
          password: credentials.password,
        },
        { requiresAuth: false }
      );
    } catch (error) {
      throw createApiError(
        'AUTH_LOGIN_FAILED',
        'Failed to login. Please check your credentials.',
        (error as any).status || 0
      );
    }
  }

  async signup(credentials: SignupCredentials): Promise<AuthResponse> {
    try {
      return await apiClient.post<AuthResponse>(
        AUTH_ENDPOINTS.SIGNUP,
        {
          email: credentials.email,
          password: credentials.password,
          name: credentials.name,
        },
        { requiresAuth: false }
      );
    } catch (error) {
      throw createApiError(
        'AUTH_SIGNUP_FAILED',
        'Unable to create account. Please try again.',
        (error as any).status || 0
      );
    }
  }

  async logout(): Promise<void> {
    await apiClient.post(AUTH_ENDPOINTS.LOGOUT);
  }

  async validateToken(token: string): Promise<TokenValidationResponse> {
    if (!token) {
      return { valid: false };
    }

    try {
      const response = await apiClient.get<{ user: any }>(AUTH_ENDPOINTS.ME, {
        requiresAuth: false,
        headers: { Authorization: `Bearer ${token}` },
      });
      return {
        valid: true,
        user: response.user,
      };
    } catch (error) {
      return { valid: false };
    }
  }

  async refreshToken(): Promise<AuthResponse> {
    return await apiClient.post<AuthResponse>(AUTH_ENDPOINTS.REFRESH);
  }
}

export const apiAuthService = new ApiAuthService();