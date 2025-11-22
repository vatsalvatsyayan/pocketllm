/**
 * Application Constants
 *
 * Centralized configuration and constants used throughout the application.
 * Using environment variables with fallback defaults.
 */

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api';
const normalizedBaseUrl = rawBaseUrl.endsWith('/v1')
  ? rawBaseUrl
  : `${rawBaseUrl.replace(/\/+$/, '')}/v1`;

/**
 * API Configuration
 */
export const API_CONFIG = {
  BASE_URL: normalizedBaseUrl,
  TIMEOUT: 30000, // 30 seconds
  MOCK_AUTH_ENABLED: import.meta.env.VITE_MOCK_AUTH === 'true',
  MOCK_CHAT_ENABLED: import.meta.env.VITE_MOCK_CHAT !== 'false', // Default to true for development
} as const;

/**
 * Authentication Configuration
 */
export const AUTH_CONFIG = {
  TOKEN_KEY: import.meta.env.VITE_AUTH_TOKEN_KEY || 'pocketllm_auth_token',
  TOKEN_EXPIRY_KEY: 'pocketllm_token_expiry',
  USER_KEY: 'pocketllm_user',
  REMEMBER_ME_DURATION: 30 * 24 * 60 * 60 * 1000, // 30 days in milliseconds
  SESSION_DURATION: 24 * 60 * 60 * 1000, // 24 hours in milliseconds
} as const;

/**
 * Application Routes
 */
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  SIGNUP: '/signup',
  CHAT: '/chat',
  CHAT_SESSION: (sessionId: string) => `/chat/${sessionId}`,
  DASHBOARD: '/dashboard', // Legacy - redirects to /chat
  PROFILE: '/profile',
  SETTINGS: '/settings',
  NOT_FOUND: '/404',
} as const;

/**
 * Validation Rules
 */
export const VALIDATION = {
  EMAIL: {
    PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    MIN_LENGTH: 5,
    MAX_LENGTH: 255,
  },
  PASSWORD: {
    MIN_LENGTH: 6,
    MAX_LENGTH: 128,
    PATTERN: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{6,}$/, // At least 1 uppercase, 1 lowercase, 1 number
    REQUIRE_STRONG: false, // Set to true to enforce strong password pattern
  },
  NAME: {
    MIN_LENGTH: 2,
    MAX_LENGTH: 100,
  },
} as const;

/**
 * Chat Configuration
 */
export const CHAT_CONFIG = {
  MAX_MESSAGE_LENGTH: 4000, // characters
  STREAM_TIMEOUT: 60000, // 60 seconds
  RETRY_ATTEMPTS: 3,
  AUTO_SCROLL_THRESHOLD: 100, // pixels from bottom
  TYPING_INDICATOR_DELAY: 300, // ms
} as const;

/**
 * UI Constants
 */
export const UI = {
  TOAST_DURATION: 5000, // 5 seconds
  DEBOUNCE_DELAY: 300, // 300ms
  ANIMATION_DURATION: 200, // 200ms
} as const;

/**
 * Error Messages
 */
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  SERVER_ERROR: 'Server error. Please try again later.',
  UNAUTHORIZED: 'Session expired. Please login again.',
  INVALID_CREDENTIALS: 'Invalid email or password.',
  EMAIL_REQUIRED: 'Email is required.',
  EMAIL_INVALID: 'Please enter a valid email address.',
  PASSWORD_REQUIRED: 'Password is required.',
  PASSWORD_TOO_SHORT: `Password must be at least ${VALIDATION.PASSWORD.MIN_LENGTH} characters.`,
  PASSWORD_TOO_WEAK: 'Password must contain uppercase, lowercase, and number.',
  PASSWORDS_DONT_MATCH: 'Passwords do not match.',
  NAME_REQUIRED: 'Name is required.',
  NAME_TOO_SHORT: `Name must be at least ${VALIDATION.NAME.MIN_LENGTH} characters.`,
  GENERIC_ERROR: 'Something went wrong. Please try again.',
  // Chat errors
  CHAT_LOAD_ERROR: 'Failed to load chat sessions.',
  MESSAGE_SEND_ERROR: 'Failed to send message. Please try again.',
  STREAM_ERROR: 'Connection lost. Please try again.',
  SESSION_LOAD_ERROR: 'Failed to load chat history.',
  MESSAGE_TOO_LONG: `Message is too long. Maximum ${CHAT_CONFIG.MAX_MESSAGE_LENGTH} characters.`,
} as const;

/**
 * Success Messages
 */
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'Successfully logged in!',
  SIGNUP_SUCCESS: 'Account created successfully!',
  LOGOUT_SUCCESS: 'Successfully logged out.',
  PROFILE_UPDATED: 'Profile updated successfully.',
  MESSAGE_SENT: 'Message sent successfully.',
  SESSION_CREATED: 'New chat started.',
} as const;

/**
 * Application Metadata
 */
export const APP_META = {
  NAME: import.meta.env.VITE_APP_NAME || 'pocketLLM Portal',
  VERSION: import.meta.env.VITE_APP_VERSION || '1.0.0',
  DESCRIPTION: 'Chat with local small language models',
} as const;
