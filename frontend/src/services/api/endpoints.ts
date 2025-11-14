/**
 * API Endpoints
 *
 * Centralized definition of all API endpoints.
 * Makes it easy to update endpoint URLs when the backend changes.
 */

import { API_CONFIG } from '../../utils/constants';

const BASE_URL = API_CONFIG.BASE_URL;

/**
 * Authentication endpoints
 */
export const AUTH_ENDPOINTS = {
  LOGIN: `${BASE_URL}/auth/login`,
  SIGNUP: `${BASE_URL}/auth/signup`,
  LOGOUT: `${BASE_URL}/auth/logout`,
  REFRESH: `${BASE_URL}/auth/refresh`,
  VALIDATE: `${BASE_URL}/auth/validate`,
  PASSWORD_RESET_REQUEST: `${BASE_URL}/auth/password-reset`,
  PASSWORD_RESET_CONFIRM: `${BASE_URL}/auth/password-reset/confirm`,
} as const;

/**
 * User endpoints
 */
export const USER_ENDPOINTS = {
  PROFILE: `${BASE_URL}/users/profile`,
  UPDATE_PROFILE: `${BASE_URL}/users/profile`,
  CHANGE_PASSWORD: `${BASE_URL}/users/change-password`,
} as const;

/**
 * LLM endpoints (placeholder for future implementation)
 */
export const LLM_ENDPOINTS = {
  CHAT: `${BASE_URL}/llm/chat`,
  MODELS: `${BASE_URL}/llm/models`,
  CONVERSATIONS: `${BASE_URL}/llm/conversations`,
} as const;
