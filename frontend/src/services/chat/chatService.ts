/**
 * Chat Service
 *
 * Handles all chat-related API calls including:
 * - Fetching chat sessions
 * - Creating new sessions
 * - Fetching message history
 * - Sending messages (non-streaming)
 *
 * Note: Streaming is handled separately in useChatStream hook
 */

import {
  ChatSession,
  ChatMessage,
  CreateSessionRequest,
  SessionListResponse,
  MessageListResponse,
  PaginationParams,
} from '../../types/chat.types';
import { apiClient } from '../api/apiClient';
import { CHAT_ENDPOINTS } from '../api/endpoints';
import { handleApiError } from '../../utils/errorHandler';
import { ERROR_MESSAGES } from '../../utils/constants';

/**
 * Chat Service Class
 */
class ChatService {

  /**
   * Get all chat sessions for the current user
   */
  async getSessions(params?: PaginationParams): Promise<SessionListResponse> {
    try {
      const queryParams = new URLSearchParams();
      
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.limit) queryParams.append('limit', params.limit.toString());
      if (params?.sortBy) queryParams.append('sortBy', params.sortBy);
      if (params?.sortOrder) queryParams.append('sortOrder', params.sortOrder);

      const url = `${CHAT_ENDPOINTS.SESSIONS}${queryParams.toString() ? `?${queryParams}` : ''}`;
      const response = await apiClient.get<SessionListResponse>(url);
      
      return response;
    } catch (error) {
      throw handleApiError(error, ERROR_MESSAGES.CHAT_LOAD_ERROR);
    }
  }

  /**
   * Get a specific chat session by ID
   */
  async getSession(sessionId: string): Promise<ChatSession> {
    try {
      const response = await apiClient.get<ChatSession>(
        CHAT_ENDPOINTS.SESSION(sessionId)
      );
      return response;
    } catch (error) {
      throw handleApiError(error, ERROR_MESSAGES.SESSION_LOAD_ERROR);
    }
  }

  /**
   * Create a new chat session
   */
  async createSession(data?: CreateSessionRequest): Promise<ChatSession> {
    try {
      const response = await apiClient.post<ChatSession>(
        CHAT_ENDPOINTS.SESSIONS,
        data || {}
      );
      return response;
    } catch (error) {
      throw handleApiError(error, 'Failed to create chat session.');
    }
  }

  /**
   * Update session metadata (e.g., title)
   */
  async updateSession(
    sessionId: string,
    data: Partial<ChatSession>
  ): Promise<ChatSession> {
    try {
      const response = await apiClient.patch<ChatSession>(
        CHAT_ENDPOINTS.SESSION(sessionId),
        data
      );
      return response;
    } catch (error) {
      throw handleApiError(error, 'Failed to update session.');
    }
  }

  /**
   * Delete a chat session
   */
  async deleteSession(sessionId: string): Promise<void> {
    try {
      await apiClient.delete(CHAT_ENDPOINTS.SESSION(sessionId));
    } catch (error) {
      throw handleApiError(error, 'Failed to delete session.');
    }
  }

  /**
   * Get messages for a specific session
   */
  async getMessages(sessionId: string): Promise<MessageListResponse> {
    try {
      const response = await apiClient.get<MessageListResponse>(
        CHAT_ENDPOINTS.SESSION_MESSAGES(sessionId)
      );
      return response;
    } catch (error) {
      throw handleApiError(error, ERROR_MESSAGES.SESSION_LOAD_ERROR);
    }
  }

  /**
   * Generate a title for a session based on first message
   * (Can be called after first message is sent)
   */
  async generateSessionTitle(sessionId: string): Promise<string> {
    try {
      const response = await apiClient.post<{ title: string }>(
        CHAT_ENDPOINTS.GENERATE_TITLE(sessionId)
      );
      return response.title;
    } catch (error) {
      // Non-critical - return default title on error
      console.error('Failed to generate title:', error);
      return 'New Chat';
    }
  }

  /**
   * Clear all messages in a session
   */
  async clearMessages(sessionId: string): Promise<void> {
    try {
      await apiClient.delete(CHAT_ENDPOINTS.CLEAR_MESSAGES(sessionId));
    } catch (error) {
      throw handleApiError(error, 'Failed to clear messages.');
    }
  }

  /**
   * Add message to session (for persistence after streaming)
   * Note: In real API, messages are typically saved on the backend during streaming
   * This method is mainly for mock service compatibility
   */
  async addMessage(message: ChatMessage): Promise<void> {
    // In real implementation, backend handles message persistence
    // This is a no-op for real API, but keeps interface consistent with mock
    return Promise.resolve();
  }
}

/**
 * Export singleton instance
 */
export const chatService = new ChatService();

