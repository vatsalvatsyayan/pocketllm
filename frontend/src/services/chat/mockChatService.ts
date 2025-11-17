/**
 * Mock Chat Service
 *
 * Mock implementation for development and testing without a backend.
 * Simulates API calls with realistic delays and data.
 *
 * Features:
 * - In-memory session and message storage
 * - Simulated streaming responses
 * - TinyLlama model responses
 * - Realistic delays
 *
 * TODO: Replace with real API when backend is ready.
 */

import {
  ChatSession,
  ChatMessage,
  CreateSessionRequest,
  SessionListResponse,
  MessageListResponse,
  PaginationParams,
} from '../../types/chat.types';

/**
 * Simulates network delay
 */
const delay = (ms: number = 800): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

/**
 * Generate unique ID
 */
const generateId = (prefix: string): string => {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Mock session storage
 */
let mockSessions: ChatSession[] = [
  {
    id: 'session_demo_1',
    userId: 'user_1',
    title: 'Welcome to pocketLLM',
    createdAt: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
    updatedAt: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
    messageCount: 2,
    lastMessage: 'Tell me about TinyLlama',
    model: 'tinyllama',
  },
  {
    id: 'session_demo_2',
    userId: 'user_1',
    title: 'AI and Machine Learning',
    createdAt: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
    updatedAt: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
    messageCount: 4,
    lastMessage: 'What is machine learning?',
    model: 'tinyllama',
  },
];

/**
 * Mock message storage
 */
const mockMessages: Record<string, ChatMessage[]> = {
  session_demo_1: [
    {
      id: 'msg_1',
      sessionId: 'session_demo_1',
      role: 'user',
      content: 'Hello! What is pocketLLM?',
      timestamp: new Date(Date.now() - 86400000).toISOString(),
      status: 'sent',
    },
    {
      id: 'msg_2',
      sessionId: 'session_demo_1',
      role: 'assistant',
      content:
        "Hello! pocketLLM is a lightweight language model platform that allows you to run small language models locally. It's designed to be efficient and privacy-focused, keeping all your data on your device.",
      timestamp: new Date(Date.now() - 86390000).toISOString(),
      status: 'sent',
    },
  ],
  session_demo_2: [
    {
      id: 'msg_3',
      sessionId: 'session_demo_2',
      role: 'user',
      content: 'What is machine learning?',
      timestamp: new Date(Date.now() - 172800000).toISOString(),
      status: 'sent',
    },
    {
      id: 'msg_4',
      sessionId: 'session_demo_2',
      role: 'assistant',
      content:
        'Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It uses algorithms to analyze data, identify patterns, and make predictions or decisions.',
      timestamp: new Date(Date.now() - 172790000).toISOString(),
      status: 'sent',
    },
  ],
};

/**
 * Mock TinyLlama responses for different prompts
 */
const getMockResponse = (prompt: string): string => {
  const lowerPrompt = prompt.toLowerCase();

  // Pattern matching for common questions
  if (lowerPrompt.includes('hello') || lowerPrompt.includes('hi')) {
    return "Hello! I'm TinyLlama, a small but capable language model. How can I help you today?";
  }

  if (lowerPrompt.includes('who are you') || lowerPrompt.includes('what are you')) {
    return "I'm TinyLlama, a 1.1B parameter language model developed to be efficient and accessible. I can help with various tasks like answering questions, writing, and general conversation!";
  }

  if (lowerPrompt.includes('tinyllama')) {
    return "TinyLlama is a compact 1.1B parameter language model trained on 3 trillion tokens. Despite its small size, it achieves impressive performance and can run efficiently on consumer hardware. It's based on the Llama architecture and is designed to be accessible for everyone!";
  }

  if (lowerPrompt.includes('ai') || lowerPrompt.includes('artificial intelligence')) {
    return 'Artificial Intelligence (AI) refers to computer systems that can perform tasks typically requiring human intelligence. This includes learning, reasoning, problem-solving, and understanding language. AI has many applications, from virtual assistants to self-driving cars!';
  }

  if (lowerPrompt.includes('machine learning') || lowerPrompt.includes('ml')) {
    return 'Machine Learning is a subset of AI where systems learn from data without explicit programming. It involves training models on datasets to recognize patterns and make predictions. Common types include supervised learning, unsupervised learning, and reinforcement learning.';
  }

  if (lowerPrompt.includes('python')) {
    return "Python is a popular high-level programming language known for its simplicity and readability. It's widely used in web development, data science, machine learning, and automation. Its extensive library ecosystem makes it versatile for many applications!";
  }

  if (lowerPrompt.includes('react')) {
    return "React is a JavaScript library for building user interfaces, developed by Facebook. It uses a component-based architecture and a virtual DOM for efficient rendering. React is popular for creating interactive and dynamic web applications!";
  }

  if (lowerPrompt.includes('help') || lowerPrompt.includes('what can you do')) {
    return "I can help with various tasks including:\n- Answering questions on many topics\n- Explaining concepts\n- Writing and editing text\n- Coding assistance\n- General conversation\n\nFeel free to ask me anything!";
  }

  // Generic response for other prompts
  return `That's an interesting question about "${prompt}". As TinyLlama, I'm here to help! While I'm a smaller model, I can assist with a wide range of topics. Could you provide more details or ask about something specific?`;
};

/**
 * Mock Chat Service Class
 */
class MockChatService {
  /**
   * Get all chat sessions
   */
  async getSessions(params?: PaginationParams): Promise<SessionListResponse> {
    await delay(600);

    // Sort sessions
    const sorted = [...mockSessions].sort((a, b) => {
      const aDate = new Date(a.updatedAt).getTime();
      const bDate = new Date(b.updatedAt).getTime();
      return bDate - aDate; // Most recent first
    });

    console.log('📋 Mock: Loaded', sorted.length, 'sessions');

    return {
      data: sorted,
      total: sorted.length,
      page: params?.page || 1,
      limit: params?.limit || 20,
      hasMore: false,
    };
  }

  /**
   * Get specific session
   */
  async getSession(sessionId: string): Promise<ChatSession> {
    await delay(400);

    const session = mockSessions.find((s) => s.id === sessionId);
    if (!session) {
      throw new Error('Session not found');
    }

    console.log('📄 Mock: Loaded session', sessionId);
    return session;
  }

  /**
   * Create new session
   */
  async createSession(data?: CreateSessionRequest): Promise<ChatSession> {
    await delay(500);

    const newSession: ChatSession = {
      id: generateId('session'),
      userId: 'user_1',
      title: data?.title || 'New Chat',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messageCount: 0,
      model: data?.model || 'tinyllama',
    };

    mockSessions.unshift(newSession);
    mockMessages[newSession.id] = [];

    console.log('✨ Mock: Created session', newSession.id);
    return newSession;
  }

  /**
   * Update session
   */
  async updateSession(
    sessionId: string,
    data: Partial<ChatSession>
  ): Promise<ChatSession> {
    await delay(400);

    const index = mockSessions.findIndex((s) => s.id === sessionId);
    if (index === -1) {
      throw new Error('Session not found');
    }

    mockSessions[index] = {
      ...mockSessions[index],
      ...data,
      updatedAt: new Date().toISOString(),
    };

    console.log('✏️ Mock: Updated session', sessionId);
    return mockSessions[index];
  }

  /**
   * Delete session
   */
  async deleteSession(sessionId: string): Promise<void> {
    await delay(400);

    const index = mockSessions.findIndex((s) => s.id === sessionId);
    if (index === -1) {
      throw new Error('Session not found');
    }

    mockSessions.splice(index, 1);
    delete mockMessages[sessionId];

    console.log('🗑️ Mock: Deleted session', sessionId);
  }

  /**
   * Get messages for session
   */
  async getMessages(sessionId: string): Promise<MessageListResponse> {
    await delay(600);

    const messages = mockMessages[sessionId] || [];

    console.log('💬 Mock: Loaded', messages.length, 'messages for session', sessionId);
    if (messages.length > 0) {
      console.log('   Messages:', messages.map(m => `${m.role}: ${m.content.substring(0, 30)}...`));
    }

    return {
      sessionId,
      messages,
      total: messages.length,
    };
  }

  /**
   * Generate session title
   */
  async generateSessionTitle(sessionId: string): Promise<string> {
    await delay(1000);

    const messages = mockMessages[sessionId];
    if (!messages || messages.length === 0) {
      return 'New Chat';
    }

    // Generate title from first user message
    const firstMessage = messages.find((m) => m.role === 'user');
    if (!firstMessage) {
      return 'New Chat';
    }

    // Take first 30 chars of message
    const title = firstMessage.content.substring(0, 30);
    const finalTitle = title.length < firstMessage.content.length ? `${title}...` : title;

    console.log('🏷️ Mock: Generated title:', finalTitle);
    return finalTitle;
  }

  /**
   * Clear messages
   */
  async clearMessages(sessionId: string): Promise<void> {
    await delay(400);

    mockMessages[sessionId] = [];
    console.log('🧹 Mock: Cleared messages for session', sessionId);
  }

  /**
   * Add message to session (for persistence after streaming)
   */
  async addMessage(message: ChatMessage): Promise<void> {
    // No delay - this is called after streaming completes
    
    if (!mockMessages[message.sessionId]) {
      mockMessages[message.sessionId] = [];
    }

    // Check if message already exists (avoid duplicates)
    const exists = mockMessages[message.sessionId].some((m) => m.id === message.id);
    if (!exists) {
      mockMessages[message.sessionId].push(message);
      console.log('💾 Mock: Saved message', message.id, 'to session', message.sessionId);
    }
  }

  /**
   * Mock streaming - this simulates server-side streaming
   * In real implementation, this would be handled by useChatStream hook
   * calling the backend streaming endpoint
   */
  async addMessageAndGetResponse(
    sessionId: string,
    userMessage: string
  ): Promise<{ userMsg: ChatMessage; assistantMsg: ChatMessage; responseText: string }> {
    await delay(300);

    // Create user message
    const userMsg: ChatMessage = {
      id: generateId('msg'),
      sessionId,
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
      status: 'sent',
    };

    // Add to storage
    if (!mockMessages[sessionId]) {
      mockMessages[sessionId] = [];
    }
    mockMessages[sessionId].push(userMsg);

    // Generate response
    const responseText = getMockResponse(userMessage);

    // Create assistant message
    const assistantMsg: ChatMessage = {
      id: generateId('msg'),
      sessionId,
      role: 'assistant',
      content: responseText,
      timestamp: new Date().toISOString(),
      status: 'sent',
    };

    // Add to storage
    mockMessages[sessionId].push(assistantMsg);

    // Update session
    const sessionIndex = mockSessions.findIndex((s) => s.id === sessionId);
    if (sessionIndex !== -1) {
      mockSessions[sessionIndex] = {
        ...mockSessions[sessionIndex],
        updatedAt: new Date().toISOString(),
        lastMessage: userMessage,
        messageCount: mockMessages[sessionId].length,
      };
    }

    console.log('💬 Mock: Added message and generated response');

    return { userMsg, assistantMsg, responseText };
  }
}

/**
 * Export singleton instance
 */
export const mockChatService = new MockChatService();

