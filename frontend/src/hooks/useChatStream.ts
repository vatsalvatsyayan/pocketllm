/**
 * useChatStream Hook
 *
 * Custom hook for handling streaming LLM responses.
 * Manages the WebSocket/SSE/Fetch streaming connection and state.
 *
 * Features:
 * - Real-time token-by-token streaming
 * - Error handling and retry logic
 * - Abort/cancel capability
 * - Timeout handling
 */

import { useState, useCallback, useRef } from 'react';
import { StreamChunk } from '../types/chat.types';
import { CHAT_ENDPOINTS } from '../services/api/endpoints';
import { getToken } from '../services/storage/tokenStorage';
import { ERROR_MESSAGES, CHAT_CONFIG, API_CONFIG } from '../utils/constants';
import { logError } from '../utils/errorHandler';
import { mockStreamResponse } from '../services/chat/mockStreamService';

/**
 * Hook state interface
 */
interface UseChatStreamState {
  isStreaming: boolean;
  error: string | null;
  currentMessageId: string | null;
}

/**
 * Hook return interface
 */
interface UseChatStreamReturn extends UseChatStreamState {
  startStream: (
    prompt: string,
    sessionId: string,
    onToken: (content: string) => void,
    onComplete: (messageId: string) => void
  ) => Promise<void>;
  stopStream: () => void;
}

/**
 * Generate unique message ID
 */
const generateMessageId = (): string => {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * useChatStream Hook
 */
export const useChatStream = (): UseChatStreamReturn => {
  const [state, setState] = useState<UseChatStreamState>({
    isStreaming: false,
    error: null,
    currentMessageId: null,
  });

  // Keep track of abort controller
  const abortControllerRef = useRef<AbortController | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Stop/abort the current stream
   */
  const stopStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }

    setState((prev) => ({
      ...prev,
      isStreaming: false,
      currentMessageId: null,
    }));
  }, []);

  /**
   * Start streaming a response
   */
  const startStream = useCallback(
    async (
      prompt: string,
      sessionId: string,
      onToken: (content: string) => void,
      onComplete: (messageId: string) => void
    ): Promise<void> => {
      // Reset state
      setState({
        isStreaming: true,
        error: null,
        currentMessageId: null,
      });

      // Create new abort controller
      abortControllerRef.current = new AbortController();
      const signal = abortControllerRef.current.signal;

      // Generate message ID
      const messageId = generateMessageId();
      setState((prev) => ({ ...prev, currentMessageId: messageId }));

      try {
        // Use mock streaming if enabled
        if (API_CONFIG.MOCK_CHAT_ENABLED) {
          await mockStreamResponse(
            prompt,
            onToken,
            onComplete,
            (error) => {
              setState((prev) => ({ ...prev, error, isStreaming: false }));
            },
            signal
          );
          stopStream();
          return;
        }
        // Get auth token
        const token = getToken();
        if (!token) {
          throw new Error(ERROR_MESSAGES.UNAUTHORIZED);
        }

        // Set timeout
        timeoutRef.current = setTimeout(() => {
          stopStream();
          setState((prev) => ({
            ...prev,
            error: 'Request timed out. Please try again.',
          }));
        }, CHAT_CONFIG.STREAM_TIMEOUT);

        // Make streaming request
        const response = await fetch(CHAT_ENDPOINTS.STREAM_MESSAGE, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            sessionId,
            prompt,
            messageId,
          }),
          signal,
        });

        // Clear timeout on successful connection
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
          timeoutRef.current = null;
        }

        // Check response status
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(
            errorData.message || ERROR_MESSAGES.MESSAGE_SEND_ERROR
          );
        }

        // Check if body is readable
        if (!response.body) {
          throw new Error('Response body is not readable');
        }

        // Create reader
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        // Read stream
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            break;
          }

          // Decode chunk
          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;

          // Process complete lines (SSE format: data: {...}\n\n)
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer

          for (const line of lines) {
            if (!line.trim()) continue;

            // Remove 'data: ' prefix if present
            const data = line.replace(/^data: /, '').trim();
            
            if (!data || data === '[DONE]') continue;

            try {
              // Parse JSON chunk
              const parsed: StreamChunk = JSON.parse(data);

              // Handle different chunk types
              switch (parsed.type) {
                case 'token':
                  if (parsed.content) {
                    onToken(parsed.content);
                  }
                  break;

                case 'error':
                  throw new Error(parsed.error || ERROR_MESSAGES.STREAM_ERROR);

                case 'end':
                  // Stream completed successfully
                  onComplete(parsed.messageId || messageId);
                  stopStream();
                  return;

                default:
                  // Ignore unknown types
                  break;
              }
            } catch (parseError) {
              // If not JSON, treat as plain text token
              if (data) {
                onToken(data);
              }
            }
          }
        }

        // Stream ended
        onComplete(messageId);
        stopStream();
      } catch (error: any) {
        // Handle abort
        if (error.name === 'AbortError') {
          setState((prev) => ({
            ...prev,
            isStreaming: false,
            error: null, // Clear error for cancellation (not an error)
          }));
          // Throw so ChatPage can save partial messages
          throw error;
        }

        // Handle other errors
        const errorMessage =
          error.message || ERROR_MESSAGES.MESSAGE_SEND_ERROR;
        
        logError(error, 'Chat Stream');
        
        setState((prev) => ({
          ...prev,
          isStreaming: false,
          error: errorMessage,
        }));

        throw error;
      } finally {
        // Cleanup
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
          timeoutRef.current = null;
        }
        abortControllerRef.current = null;
      }
    },
    [stopStream]
  );

  return {
    ...state,
    startStream,
    stopStream,
  };
};

