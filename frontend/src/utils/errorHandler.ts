/**
 * Error Handling Utilities
 *
 * Centralized error handling and parsing logic.
 * Converts various error types into user-friendly messages.
 */

import { ApiError } from '../types/api.types';
import { ERROR_MESSAGES } from './constants';

/**
 * Extracts error message from various error types
 */
export const getErrorMessage = (error: unknown): string => {
  // Handle ApiError
  if (isApiError(error)) {
    return error.message || ERROR_MESSAGES.GENERIC_ERROR;
  }

  // Handle Error object
  if (error instanceof Error) {
    return error.message;
  }

  // Handle string errors
  if (typeof error === 'string') {
    return error;
  }

  // Handle object with message property
  if (error && typeof error === 'object' && 'message' in error) {
    return String(error.message);
  }

  // Default fallback
  return ERROR_MESSAGES.GENERIC_ERROR;
};

/**
 * Type guard for ApiError
 */
export const isApiError = (error: unknown): error is ApiError => {
  return (
    typeof error === 'object' &&
    error !== null &&
    'code' in error &&
    'message' in error
  );
};

/**
 * Checks if error is a network error
 */
export const isNetworkError = (error: unknown): boolean => {
  if (error instanceof Error) {
    return (
      error.message.includes('network') ||
      error.message.includes('fetch') ||
      error.message.includes('Network')
    );
  }
  return false;
};

/**
 * Checks if error is an authentication error
 */
export const isAuthError = (error: unknown): boolean => {
  if (isApiError(error)) {
    return error.statusCode === 401 || error.code === 'UNAUTHORIZED';
  }
  return false;
};

/**
 * Creates a standardized ApiError object
 */
export const createApiError = (
  code: string,
  message: string,
  statusCode?: number,
  details?: Record<string, any>
): ApiError => {
  return {
    code,
    message,
    statusCode,
    details,
  };
};

/**
 * Handles API errors and returns appropriate user message
 */
export const handleApiError = (error: unknown): string => {
  if (isNetworkError(error)) {
    return ERROR_MESSAGES.NETWORK_ERROR;
  }

  if (isAuthError(error)) {
    return ERROR_MESSAGES.UNAUTHORIZED;
  }

  if (isApiError(error)) {
    // Map specific error codes to user-friendly messages
    switch (error.code) {
      case 'INVALID_CREDENTIALS':
        return ERROR_MESSAGES.INVALID_CREDENTIALS;
      case 'USER_NOT_FOUND':
        return ERROR_MESSAGES.INVALID_CREDENTIALS; // Don't reveal user existence
      case 'EMAIL_ALREADY_EXISTS':
        return 'An account with this email already exists.';
      case 'VALIDATION_ERROR':
        return error.message || 'Please check your input and try again.';
      default:
        return error.message || ERROR_MESSAGES.SERVER_ERROR;
    }
  }

  return getErrorMessage(error);
};

/**
 * Logs error for debugging (can be extended to send to monitoring service)
 */
export const logError = (error: unknown, context?: string): void => {
  if (import.meta.env.DEV) {
    console.error(`[Error${context ? ` - ${context}` : ''}]:`, error);
  }

  // TODO: In production, send to error monitoring service (e.g., Sentry)
  // if (import.meta.env.PROD) {
  //   sendToMonitoringService(error, context);
  // }
};
