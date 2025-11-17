/**
 * MessageBubble Component
 *
 * Displays an individual chat message with appropriate styling
 * based on the sender (user or assistant).
 *
 * Features:
 * - Different styling for user vs assistant messages
 * - Streaming indicator for messages being generated
 * - Error state display
 * - Markdown support (future enhancement)
 */

import React from 'react';
import { User, Bot, AlertCircle } from 'lucide-react';
import { ChatMessage } from '../../types/chat.types';
import { cn } from '../../utils/cn';

/**
 * MessageBubble Props
 */
interface MessageBubbleProps {
  message: ChatMessage;
  isStreaming?: boolean;
}

/**
 * MessageBubble Component
 */
export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  isStreaming = false,
}) => {
  const isUser = message.role === 'user';
  const isError = message.status === 'error';

  return (
    <div
      className={cn(
        'flex gap-3 mb-4',
        isUser ? 'justify-end' : 'justify-start'
      )}
    >
      {/* Avatar - only show for assistant */}
      {!isUser && (
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-lg">
            <Bot size={18} className="text-white" />
          </div>
        </div>
      )}

      {/* Message Content */}
      <div
        className={cn(
          'max-w-[70%] rounded-2xl px-4 py-3 shadow-md',
          isUser
            ? 'bg-gradient-to-br from-primary-600 to-primary-500 text-white'
            : isError
            ? 'bg-red-500/10 border border-red-500/30 text-red-200'
            : 'bg-dark-800 text-dark-100 border border-dark-700'
        )}
      >
        {/* Error Icon */}
        {isError && (
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle size={16} className="text-red-400" />
            <span className="text-sm font-medium text-red-400">Error</span>
          </div>
        )}

        {/* Message Text */}
        <div className="whitespace-pre-wrap break-words">
          {message.content || (isStreaming && '...')}
        </div>

        {/* Streaming Indicator */}
        {isStreaming && message.content && (
          <span className="inline-block w-2 h-4 ml-1 bg-current animate-pulse" />
        )}

        {/* Error Message */}
        {isError && message.error && (
          <div className="mt-2 text-sm text-red-300 italic">
            {message.error}
          </div>
        )}

        {/* Timestamp */}
        <div
          className={cn(
            'text-xs mt-2',
            isUser ? 'text-primary-100' : 'text-dark-400'
          )}
        >
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>

      {/* Avatar - only show for user */}
      {isUser && (
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-accent-500 to-accent-600 flex items-center justify-center shadow-lg">
            <User size={18} className="text-white" />
          </div>
        </div>
      )}
    </div>
  );
};

