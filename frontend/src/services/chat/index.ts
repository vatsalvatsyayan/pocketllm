/**
 * Chat Service Export
 *
 * Switches between mock and real chat service based on environment configuration.
 * Similar to auth service pattern.
 *
 * To use real API:
 * - Set VITE_MOCK_CHAT=false in .env.local
 *
 * To use mock API (default for development):
 * - Set VITE_MOCK_CHAT=true or leave unset
 */

import { API_CONFIG } from '../../utils/constants';
import { chatService as realChatService } from './chatService';
import { mockChatService } from './mockChatService';

/**
 * Export the appropriate service based on configuration
 */
export const chatService = API_CONFIG.MOCK_CHAT_ENABLED
  ? mockChatService
  : realChatService;

/**
 * Log which service is being used
 */
if (API_CONFIG.MOCK_CHAT_ENABLED) {
  console.log('🎭 Using MOCK chat service (for development)');
} else {
  console.log('🌐 Using REAL chat service');
}

