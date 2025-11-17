/**
 * API Client
 *
 * Wrapper around fetch API with interceptors for authentication,
 * error handling, and request/response transformation.
 * This abstraction makes it easy to switch to axios or other HTTP clients.
 */

import { ApiError } from '../../types/api.types';
import { getToken } from '../storage/tokenStorage';
import { createApiError } from '../../utils/errorHandler';

/**
 * Request configuration
 */
interface RequestConfig extends RequestInit {
  requiresAuth?: boolean;
}

/**
 * Makes an HTTP request with authentication and error handling
 */
const request = async <T = any>(
  url: string,
  config: RequestConfig = {}
): Promise<T> => {
  const { requiresAuth = true, headers = {}, ...restConfig } = config;

  // Build headers
  const requestHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(headers as Record<string, string>),
  };

  // Add authentication token if required
  if (requiresAuth) {
    const token = getToken();
    if (token) {
      requestHeaders['Authorization'] = `Bearer ${token}`;
    }
  }

  try {
    const response = await fetch(url, {
      ...restConfig,
      headers: requestHeaders,
    });

    // Parse response
    const data = await response.json().catch(() => null);

    // Handle non-2xx responses
    if (!response.ok) {
      const error: ApiError = createApiError(
        data?.code || 'REQUEST_FAILED',
        data?.message || response.statusText || 'Request failed',
        response.status,
        data?.details
      );
      throw error;
    }

    return data;
  } catch (error) {
    // Re-throw ApiError as-is
    if ((error as any).code && (error as any).message) {
      throw error;
    }

    // Handle network errors
    if (error instanceof TypeError) {
      throw createApiError(
        'NETWORK_ERROR',
        'Network error. Please check your connection.',
        0
      );
    }

    // Handle other errors
    throw createApiError(
      'UNKNOWN_ERROR',
      error instanceof Error ? error.message : 'An unknown error occurred',
      0
    );
  }
};

/**
 * HTTP GET request
 */
export const get = <T = any>(url: string, config?: RequestConfig): Promise<T> => {
  return request<T>(url, { ...config, method: 'GET' });
};

/**
 * HTTP POST request
 */
export const post = <T = any>(
  url: string,
  data?: any,
  config?: RequestConfig
): Promise<T> => {
  return request<T>(url, {
    ...config,
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });
};

/**
 * HTTP PUT request
 */
export const put = <T = any>(
  url: string,
  data?: any,
  config?: RequestConfig
): Promise<T> => {
  return request<T>(url, {
    ...config,
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  });
};

/**
 * HTTP PATCH request
 */
export const patch = <T = any>(
  url: string,
  data?: any,
  config?: RequestConfig
): Promise<T> => {
  return request<T>(url, {
    ...config,
    method: 'PATCH',
    body: data ? JSON.stringify(data) : undefined,
  });
};

/**
 * HTTP DELETE request
 */
export const del = <T = any>(url: string, config?: RequestConfig): Promise<T> => {
  return request<T>(url, { ...config, method: 'DELETE' });
};

/**
 * Export all methods as apiClient
 */
export const apiClient = {
  get,
  post,
  put,
  patch,
  delete: del,
};
