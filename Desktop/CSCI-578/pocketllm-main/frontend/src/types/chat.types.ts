/**
 * Chat Type Definitions
 *
 * Defines all chat-related types including messages, sessions, and streaming states.
 * These types form the contract between frontend and backend chat API.
 */

/**
 * Message role - who sent the message
 */
export type MessageRole = 'user' | 'assistant' | 'system';

/**
 * Message status - current state of the message
 */
export type MessageStatus = 'sending' | 'sent' | 'error' | 'streaming';

/**
 * Individual chat message
 */
export interface ChatMessage {
  id: string;
  sessionId: string;
  role: MessageRole;
  content: string;
  timestamp: string; // ISO 8601 format
  status?: MessageStatus;
  error?: string;
}

/**
 * Chat session metadata
 */
export interface ChatSession {
  id: string;
  userId: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messageCount?: number;
  lastMessage?: string; // Preview of last message
  model?: string; // Which LLM model was used
}

/**
 * Request to create a new chat session
 */
export interface CreateSessionRequest {
  title?: string;
  model?: string;
}

/**
 * Request to send a message
 */
export interface SendMessageRequest {
  sessionId: string;
  prompt: string;
  model?: string;
}

/**
 * Response from sending a message (non-streaming)
 */
export interface SendMessageResponse {
  message: ChatMessage;
  session: ChatSession;
}

/**
 * Streaming chunk received during response
 */
export interface StreamChunk {
  type: 'start' | 'token' | 'end' | 'error';
  content?: string;
  messageId?: string;
  error?: string;
  metadata?: Record<string, any>;
}

/**
 * Streaming state
 */
export interface StreamingState {
  isStreaming: boolean;
  currentMessageId: string | null;
  error: string | null;
  abortController: AbortController | null;
}

/**
 * Chat state for UI management
 */
export interface ChatState {
  sessions: ChatSession[];
  currentSession: ChatSession | null;
  messages: ChatMessage[];
  isLoading: boolean;
  isLoadingMessages: boolean;
  error: string | null;
  streamingState: StreamingState;
}

/**
 * Pagination parameters for fetching sessions
 */
export interface PaginationParams {
  page?: number;
  limit?: number;
  sortBy?: 'createdAt' | 'updatedAt';
  sortOrder?: 'asc' | 'desc';
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

/**
 * Session list response
 */
export type SessionListResponse = PaginatedResponse<ChatSession>;

/**
 * Message list response
 */
export interface MessageListResponse {
  sessionId: string;
  messages: ChatMessage[];
  total: number;
}

