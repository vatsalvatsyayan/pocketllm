/**
 * ChatThread Component
 *
 * Displays the list of chat messages with auto-scrolling behavior.
 *
 * Features:
 * - Renders all messages in chronological order
 * - Auto-scroll to bottom on new messages
 * - Loading state with skeleton
 * - Empty state when no messages
 * - Scroll-to-bottom button when scrolled up
 */

import React, { useEffect, useRef, useState } from 'react';
import { MessageSquare, ArrowDown } from 'lucide-react';
import { ChatMessage } from '../../types/chat.types';
import { MessageBubble } from './MessageBubble';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { CHAT_CONFIG } from '../../utils/constants';
import { cn } from '../../utils/cn';

/**
 * ChatThread Props
 */
interface ChatThreadProps {
  messages: ChatMessage[];
  isLoading?: boolean;
  streamingMessageId?: string | null;
}

/**
 * ChatThread Component
 */
export const ChatThread: React.FC<ChatThreadProps> = ({
  messages,
  isLoading = false,
  streamingMessageId = null,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [isAutoScrollEnabled, setIsAutoScrollEnabled] = useState(true);

  /**
   * Check if user has scrolled up
   */
  const checkScroll = () => {
    const container = containerRef.current;
    if (!container) return;

    const { scrollTop, scrollHeight, clientHeight } = container;
    const distanceFromBottom = scrollHeight - scrollTop - clientHeight;

    // Show scroll button if more than threshold away from bottom
    setShowScrollButton(distanceFromBottom > CHAT_CONFIG.AUTO_SCROLL_THRESHOLD);
    
    // Disable auto-scroll if user has scrolled up
    setIsAutoScrollEnabled(distanceFromBottom < CHAT_CONFIG.AUTO_SCROLL_THRESHOLD);
  };

  /**
   * Scroll to bottom smoothly
   */
  const scrollToBottom = (smooth = true) => {
    bottomRef.current?.scrollIntoView({
      behavior: smooth ? 'smooth' : 'auto',
    });
  };

  /**
   * Auto-scroll on new messages (if enabled)
   */
  useEffect(() => {
    if (isAutoScrollEnabled) {
      scrollToBottom(true);
    }
  }, [messages, isAutoScrollEnabled]);

  /**
   * Scroll to bottom when component mounts
   */
  useEffect(() => {
    scrollToBottom(false);
  }, []);

  /**
   * Handle scroll button click
   */
  const handleScrollToBottom = () => {
    setIsAutoScrollEnabled(true);
    scrollToBottom(true);
  };

  // Loading state
  if (isLoading && messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center bg-dark-900">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-dark-400">Loading messages...</p>
        </div>
      </div>
    );
  }

  // Empty state
  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center bg-dark-900">
        <div className="text-center max-w-md px-6">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-lg">
            <MessageSquare size={32} className="text-white" />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">
            Start a Conversation
          </h3>
          <p className="text-dark-400">
            Type a message below to chat with the AI assistant.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 relative bg-dark-900 overflow-hidden">
      {/* Messages Container */}
      <div
        ref={containerRef}
        onScroll={checkScroll}
        className="h-full overflow-y-auto scrollbar-thin scrollbar-thumb-dark-700 scrollbar-track-dark-900"
      >
        <div className="max-w-4xl mx-auto px-4 py-6">
          {/* Messages */}
          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              isStreaming={streamingMessageId === message.id}
            />
          ))}

          {/* Bottom anchor for scrolling */}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Scroll to Bottom Button */}
      {showScrollButton && (
        <button
          onClick={handleScrollToBottom}
          className={cn(
            'absolute bottom-6 right-6',
            'w-12 h-12 rounded-full',
            'bg-primary-600 hover:bg-primary-700',
            'text-white shadow-lg',
            'flex items-center justify-center',
            'transition-all duration-200',
            'hover:scale-110 active:scale-95',
            'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-dark-900'
          )}
          aria-label="Scroll to bottom"
        >
          <ArrowDown size={20} />
        </button>
      )}
    </div>
  );
};

