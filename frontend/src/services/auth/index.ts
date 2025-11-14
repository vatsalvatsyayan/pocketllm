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

import { mockAuthService } from './mockAuthService';
// TODO: Import real API service when ready
// import { apiAuthService } from './apiAuthService';

/**
 * Active authentication service
 * Change this export to switch implementations
 */
export const authService = mockAuthService;

// When real API is ready, uncomment this line and comment out the above:
// export const authService = apiAuthService;

/**
 * Export the interface for type safety
 */
export type { IAuthService } from './authService.interface';
