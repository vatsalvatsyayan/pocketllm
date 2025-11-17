/**
 * ChatPage Component
 *
 * Main chat interface that brings together all chat components.
 * Handles state management, API calls, and routing.
 *
 * Features:
 * - Session management (create, load, delete)
 * - Message management (load, send, stream)
 * - Real-time streaming responses
 * - Error handling
 * - Loading states
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { LogOut } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useChatStream } from '../hooks/useChatStream';
import { chatService } from '../services/chat';
import { ChatSession, ChatMessage } from '../types/chat.types';
import { SessionList } from '../components/chat/SessionList';
import { ChatThread } from '../components/chat/ChatThread';
import { Composer } from '../components/chat/Composer';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';
import { ROUTES, ERROR_MESSAGES } from '../utils/constants';
import { logError } from '../utils/errorHandler';

/**
 * ChatPage Component
 */
export const ChatPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId?: string }>();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { isStreaming, startStream, stopStream } = useChatStream();

  // State
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoadingSessions, setIsLoadingSessions] = useState(true);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  const [isCreatingSession, setIsCreatingSession] = useState(false);

  /**
   * Load all sessions on mount
   */
  useEffect(() => {
    loadSessions();
    
    // Info message for mock mode
    if (sessionId) {
      console.log('💡 Note: Mock storage resets on refresh. Old session IDs may not exist.');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /**
   * Load messages when sessionId changes
   */
  useEffect(() => {
    // Don't reload if we're in the middle of creating a new session
    if (isCreatingSession) {
      return;
    }

    if (sessionId) {
      loadSession(sessionId);
    } else {
      // No session selected - clear messages
      setCurrentSession(null);
      setMessages([]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, isCreatingSession]);

  /**
   * Load all sessions
   */
  const loadSessions = async () => {
    setIsLoadingSessions(true);
    setError(null);

    try {
      const response = await chatService.getSessions({
        sortBy: 'updatedAt',
        sortOrder: 'desc',
      });
      setSessions(response.data);
    } catch (err) {
      logError(err, 'Load sessions');
      setError(ERROR_MESSAGES.CHAT_LOAD_ERROR);
    } finally {
      setIsLoadingSessions(false);
    }
  };

  /**
   * Load specific session and its messages
   */
  const loadSession = async (sid: string) => {
    setIsLoadingMessages(true);
    setError(null);

    try {
      // Load session details
      const session = await chatService.getSession(sid);
      setCurrentSession(session);

      // Load messages
      const response = await chatService.getMessages(sid);
      setMessages(response.messages);
    } catch (err) {
      logError(err, 'Load session');
      
      // If session not found, silently redirect (common with mock storage after refresh)
      if ((err as any).message?.includes('not found') || (err as any).statusCode === 404) {
        console.log('Session not found, redirecting to /chat');
        navigate(ROUTES.CHAT, { replace: true });
      } else {
        // Show error only for other issues
        setError(ERROR_MESSAGES.SESSION_LOAD_ERROR);
      }
    } finally {
      setIsLoadingMessages(false);
    }
  };

  /**
   * Handle new chat
   */
  const handleNewChat = () => {
    navigate(ROUTES.CHAT);
    setCurrentSession(null);
    setMessages([]);
    setError(null);
  };

  /**
   * Handle delete session
   */
  const handleDeleteSession = async (sid: string) => {
    try {
      await chatService.deleteSession(sid);
      
      // Remove from list
      setSessions((prev) => prev.filter((s) => s.id !== sid));
      
      // If deleting current session, redirect to chat
      if (sid === sessionId) {
        navigate(ROUTES.CHAT);
      }
    } catch (err) {
      logError(err, 'Delete session');
      setError('Failed to delete session.');
    }
  };

  /**
   * Handle send message
   */
  const handleSendMessage = async (prompt: string) => {
    setError(null);

    try {
      let sid = currentSession?.id;

      // Create session if needed (first message)
      if (!sid) {
        setIsCreatingSession(true);
        const newSession = await chatService.createSession({
          title: 'New Chat',
        });
        sid = newSession.id;
        setCurrentSession(newSession);
        
        // Add to sessions list
        setSessions((prev) => [newSession, ...prev]);
        
        // Navigate to new session (but prevent reload via flag)
        navigate(ROUTES.CHAT_SESSION(sid), { replace: true });
      }

      // Create user message (optimistic update)
      const userMessage: ChatMessage = {
        id: `temp-${Date.now()}`,
        sessionId: sid,
        role: 'user',
        content: prompt,
        timestamp: new Date().toISOString(),
        status: 'sent',
      };
      setMessages((prev) => [...prev, userMessage]);

      // Create empty assistant message
      const assistantMessageId = `msg-${Date.now()}`;
      const assistantMessage: ChatMessage = {
        id: assistantMessageId,
        sessionId: sid,
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
        status: 'streaming',
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setStreamingMessageId(assistantMessageId);

      // Track assistant message content during streaming
      let assistantContent = '';

      // Helper function to save messages and update session
      const saveMessagesAndUpdateSession = async (status: 'sent' | 'cancelled') => {
        const finalAssistantMessage: ChatMessage = {
          id: assistantMessageId,
          sessionId: sid,
          role: 'assistant',
          content: assistantContent || '(cancelled)',
          timestamp: new Date().toISOString(),
          status: 'sent',
        };

        // Update UI
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId
              ? finalAssistantMessage
              : msg
          )
        );
        
        setStreamingMessageId(null);
        
        // Persist messages to mock service storage
        try {
          await chatService.addMessage(userMessage);
          if (assistantContent) {
            // Only save assistant message if it has content
            await chatService.addMessage(finalAssistantMessage);
          }
          console.log(`✅ Persisted messages to storage (${status})`);
        } catch (err) {
          console.error('❌ Failed to persist messages:', err);
        }
        
        // Update session in list
        setSessions((prev) => {
          const updated = prev.map((s) =>
            s.id === sid
              ? { 
                  ...s, 
                  updatedAt: new Date().toISOString(), 
                  lastMessage: prompt, 
                  messageCount: assistantContent ? (s.messageCount || 0) + 2 : (s.messageCount || 0) + 1
                }
              : s
          );
          return updated.sort((a, b) => 
            new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
          );
        });

        // Generate title if first message
        if (messages.length === 0) {
          generateTitle(sid);
        }

        // Clear the creating flag
        setIsCreatingSession(false);
      };

      // Start streaming
      try {
        await startStream(
          prompt,
          sid,
          // On token received
          (token: string) => {
            assistantContent += token;
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMessageId
                  ? { ...msg, content: assistantContent }
                  : msg
              )
            );
          },
          // On complete
          async () => {
            await saveMessagesAndUpdateSession('sent');
          }
        );
      } catch (err: any) {
        // Check if it was cancelled (AbortError)
        if (err.name === 'AbortError' || err.message?.includes('cancel')) {
          console.log('🛑 Stream cancelled by user');
          await saveMessagesAndUpdateSession('cancelled');
        } else {
          throw err; // Re-throw other errors
        }
      }
    } catch (err) {
      logError(err, 'Send message');
      setError(ERROR_MESSAGES.MESSAGE_SEND_ERROR);
      setStreamingMessageId(null);
      setIsCreatingSession(false);
      
      // Mark last message as error
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last && last.role === 'assistant') {
          return [
            ...prev.slice(0, -1),
            { ...last, status: 'error', error: ERROR_MESSAGES.MESSAGE_SEND_ERROR },
          ];
        }
        return prev;
      });
    }
  };

  /**
   * Generate session title based on first message
   */
  const generateTitle = async (sid: string) => {
    try {
      const title = await chatService.generateSessionTitle(sid);
      
      // Update session title in list
      setSessions((prev) =>
        prev.map((s) => (s.id === sid ? { ...s, title } : s))
      );
      
      // Update current session
      if (currentSession?.id === sid) {
        setCurrentSession((prev) => (prev ? { ...prev, title } : null));
      }
    } catch (err) {
      // Non-critical error - just log it
      logError(err, 'Generate title');
    }
  };

  /**
   * Handle logout
   */
  const handleLogout = async () => {
    await logout();
    navigate(ROUTES.LOGIN);
  };

  return (
    <div className="h-screen flex flex-col bg-dark-900">
      {/* Header */}
      <header className="h-16 border-b border-dark-800 bg-dark-900 flex items-center justify-between px-6">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">
            pocketLLM
          </h1>
          <span className="text-dark-600">|</span>
          <span className="text-dark-400 text-sm">
            {currentSession?.title || 'New Chat'}
          </span>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-sm text-dark-400">
            {user?.name || user?.email}
          </span>
          <Button
            onClick={handleLogout}
            variant="ghost"
            size="sm"
            className="gap-2"
          >
            <LogOut size={16} />
            Logout
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <SessionList
          sessions={sessions}
          activeSessionId={sessionId}
          isLoading={isLoadingSessions}
          onNewChat={handleNewChat}
          onDeleteSession={handleDeleteSession}
        />

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Error Alert */}
          {error && (
            <div className="p-4">
              <Alert variant="error" onClose={() => setError(null)}>
                {error}
              </Alert>
            </div>
          )}

          {/* Messages */}
          <ChatThread
            messages={messages}
            isLoading={isLoadingMessages}
            streamingMessageId={streamingMessageId}
          />

          {/* Input */}
          <Composer
            onSend={handleSendMessage}
            onCancel={stopStream}
            isStreaming={isStreaming}
            placeholder={
              currentSession
                ? 'Type your message...'
                : 'Start a new conversation...'
            }
          />
        </div>
      </div>
    </div>
  );
};

