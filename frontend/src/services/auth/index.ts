/**
 * Authentication Service Export
 *
 * This is the SINGLE place where you switch between mock and real API.
 *
 * TO SWITCH TO REAL API:
 * 1. Create apiAuthService.ts that implements IAuthService
 * 2. Import it here: import { apiAuthService } from './apiAuthService';
 * 3. Change the export below: export const authService = apiAuthService;
 * 4. That's it! All components will automatically use the real API.
 *
 * Current implementation: MOCK (for development)
 */

import { API_CONFIG } from '../../utils/constants';
import { apiAuthService } from './apiAuthService';
import { mockAuthService } from './mockAuthService';

/**
 * Active authentication service
 */
export const authService = API_CONFIG.MOCK_AUTH_ENABLED
	? mockAuthService
	: apiAuthService;

if (API_CONFIG.MOCK_AUTH_ENABLED) {
	console.log('🎭 Using MOCK auth service (development)');
} else {
	console.log('🔐 Using REAL auth service (JWT)');
}

/**
 * Export the interface for type safety
 */
export type { IAuthService } from './authService.interface';
