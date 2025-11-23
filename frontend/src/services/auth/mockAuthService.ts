/**
 * Mock Authentication Service
 *
 * Mock implementation of IAuthService for development.
 * Simulates API calls with realistic delays and validation.
 *
 * This service uses in-memory storage and hard-coded test users.
 * Perfect for development, testing, and demos without a backend.
 *
 * TODO: Replace this with ApiAuthService when backend is ready.
 * See login_signup_plan.md for integration instructions.
 */

import { IAuthService } from './authService.interface';
import {
  LoginCredentials,
  SignupCredentials,
  AuthResponse,
  TokenValidationResponse,
} from '../../types/auth.types';
import { User } from '../../types/user.types';
import { createApiError } from '../../utils/errorHandler';

/**
 * Simulates network delay
 */
const delay = (ms: number = 1000): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

/**
 * Mock user database (in-memory)
 */
const mockUsers: User[] = [
  {
    id: '1',
    email: 'demo@pocketllm.com',
    name: 'Demo User',
    createdAt: new Date().toISOString(),
    is_admin: true,
  },
  {
    id: '2',
    email: 'admin@pocketllm.com',
    name: 'Admin User',
    createdAt: new Date().toISOString(),
    is_admin: true,
  },
];

/**
 * Mock password storage (DO NOT DO THIS IN PRODUCTION!)
 * In real implementation, passwords are hashed on the backend
 */
const mockPasswords: Record<string, string> = {
  'demo@pocketllm.com': 'demo123',
  'admin@pocketllm.com': 'admin123',
};

/**
 * Generates a mock JWT token
 */
const generateMockToken = (userId: string): string => {
  // In real implementation, this would be a proper JWT from the server
  const timestamp = Date.now();
  return `mock-jwt-token-${userId}-${timestamp}`;
};

/**
 * Mock Authentication Service Implementation
 */
export class MockAuthService implements IAuthService {
  /**
   * Mock login implementation
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // Simulate API delay
    await delay(1000);

    // Find user by email
    const user = mockUsers.find((u) => u.email === credentials.email);

    // Validate credentials
    if (!user || mockPasswords[credentials.email] !== credentials.password) {
      throw createApiError(
        'INVALID_CREDENTIALS',
        'Invalid email or password',
        401
      );
    }

    // Generate token
    const token = generateMockToken(user.id);

    console.log('✅ Mock Login Successful:', { email: user.email, name: user.name });

    return {
      token,
      user,
      expiresIn: 86400, // 24 hours
    };
  }

  /**
   * Mock signup implementation
   */
  async signup(credentials: SignupCredentials): Promise<AuthResponse> {
    // Simulate API delay
    await delay(1200);

    // Check if email already exists
    if (mockUsers.some((u) => u.email === credentials.email)) {
      throw createApiError(
        'EMAIL_ALREADY_EXISTS',
        'An account with this email already exists',
        409
      );
    }

    // Create new user
    const newUser: User = {
      id: (mockUsers.length + 1).toString(),
      email: credentials.email,
      name: credentials.name,
      createdAt: new Date().toISOString(),
      is_admin: false,
    };

    // Add to mock database
    mockUsers.push(newUser);
    mockPasswords[credentials.email] = credentials.password;

    // Generate token
    const token = generateMockToken(newUser.id);

    console.log('✅ Mock Signup Successful:', { email: newUser.email, name: newUser.name });

    return {
      token,
      user: newUser,
      expiresIn: 86400, // 24 hours
    };
  }

  /**
   * Mock logout implementation
   */
  async logout(): Promise<void> {
    // Simulate API delay
    await delay(500);

    console.log('✅ Mock Logout Successful');

    // In real implementation, this might invalidate the token on the server
    return Promise.resolve();
  }

  /**
   * Mock token validation
   */
  async validateToken(token: string): Promise<TokenValidationResponse> {
    // Simulate API delay
    await delay(300);

    // Extract user ID from mock token
    const tokenParts = token.split('-');
    const userId = tokenParts[3];

    if (!userId) {
      return { valid: false };
    }

    // Find user
    const user = mockUsers.find((u) => u.id === userId);

    if (!user) {
      return { valid: false };
    }

    return {
      valid: true,
      user,
    };
  }

  /**
   * Mock token refresh
   */
  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    // Simulate API delay
    await delay(500);

    // Extract user ID from refresh token
    const tokenParts = refreshToken.split('-');
    const userId = tokenParts[3];

    const user = mockUsers.find((u) => u.id === userId);

    if (!user) {
      throw createApiError('INVALID_TOKEN', 'Invalid refresh token', 401);
    }

    // Generate new token
    const token = generateMockToken(user.id);

    return {
      token,
      user,
      expiresIn: 86400,
    };
  }
}

/**
 * Export singleton instance
 */
export const mockAuthService = new MockAuthService();
