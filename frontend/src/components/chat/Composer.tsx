/**
 * Composer Component
 *
 * Message input component for sending chat messages.
 *
 * Features:
 * - Auto-resizing textarea
 * - Character limit validation
 * - Disabled state during streaming
 * - Send on Enter (Shift+Enter for new line)
 * - Cancel button during streaming
 */

import React, { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { Send, StopCircle } from 'lucide-react';
import { Button } from '../ui/Button';
import { CHAT_CONFIG, ERROR_MESSAGES } from '../../utils/constants';
import { cn } from '../../utils/cn';

/**
 * Composer Props
 */
interface ComposerProps {
  onSend: (message: string) => void;
  onCancel?: () => void;
  isStreaming?: boolean;
  isDisabled?: boolean;
  placeholder?: string;
}

/**
 * Composer Component
 */
export const Composer: React.FC<ComposerProps> = ({
  onSend,
  onCancel,
  isStreaming = false,
  isDisabled = false,
  placeholder = 'Type your message...',
}) => {
  const [message, setMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  /**
   * Auto-resize textarea
   */
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    // Reset height to auto to get correct scrollHeight
    textarea.style.height = 'auto';
    
    // Set height based on content (max 200px)
    const newHeight = Math.min(textarea.scrollHeight, 200);
    textarea.style.height = `${newHeight}px`;
  }, [message]);

  /**
   * Focus textarea on mount
   */
  useEffect(() => {
    if (!isStreaming && !isDisabled) {
      textareaRef.current?.focus();
    }
  }, [isStreaming, isDisabled]);

  /**
   * Handle message change
   */
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    
    // Check length
    if (value.length > CHAT_CONFIG.MAX_MESSAGE_LENGTH) {
      setError(ERROR_MESSAGES.MESSAGE_TOO_LONG);
      return;
    }

    setMessage(value);
    setError(null);
  };

  /**
   * Handle send
   */
  const handleSend = () => {
    const trimmed = message.trim();

    // Validate
    if (!trimmed) {
      return;
    }

    if (trimmed.length > CHAT_CONFIG.MAX_MESSAGE_LENGTH) {
      setError(ERROR_MESSAGES.MESSAGE_TOO_LONG);
      return;
    }

    // Send message
    onSend(trimmed);
    
    // Clear input
    setMessage('');
    setError(null);

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  /**
   * Handle keyboard shortcuts
   */
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  /**
   * Handle cancel
   */
  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
  };

  const canSend = message.trim().length > 0 && !isStreaming && !isDisabled;

  return (
    <div className="border-t border-dark-700 bg-dark-900 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Error Message */}
        {error && (
          <div className="mb-2 text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg px-3 py-2">
            {error}
          </div>
        )}

        {/* Input Container */}
        <div className="flex gap-3 items-end">
          {/* Textarea */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={handleChange}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={isDisabled}
              rows={1}
              className={cn(
                'w-full px-4 py-3 rounded-xl resize-none',
                'bg-dark-800 border border-dark-700',
                'text-white placeholder-dark-400',
                'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
                'transition-all duration-200',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                'overflow-y-auto scrollbar-thin scrollbar-thumb-dark-600 scrollbar-track-dark-800'
              )}
              style={{
                minHeight: '48px',
                maxHeight: '200px',
              }}
            />

            {/* Character Counter */}
            <div className="absolute bottom-1 right-2 text-xs text-dark-500">
              {message.length}/{CHAT_CONFIG.MAX_MESSAGE_LENGTH}
            </div>
          </div>

          {/* Send/Cancel Button */}
          {isStreaming ? (
            <Button
              onClick={handleCancel}
              variant="danger"
              size="lg"
              className="px-4"
              aria-label="Stop generation"
            >
              <StopCircle size={20} />
            </Button>
          ) : (
            <Button
              onClick={handleSend}
              variant="primary"
              size="lg"
              disabled={!canSend}
              className="px-4"
              aria-label="Send message"
            >
              <Send size={20} />
            </Button>
          )}
        </div>

        {/* Helper Text */}
        <div className="mt-2 text-xs text-dark-500 text-center">
          Press <kbd className="px-1.5 py-0.5 bg-dark-800 rounded border border-dark-600">Enter</kbd> to send,{' '}
          <kbd className="px-1.5 py-0.5 bg-dark-800 rounded border border-dark-600">Shift + Enter</kbd> for new line
        </div>
      </div>
    </div>
  );
};

