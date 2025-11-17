/**
 * SessionList Component
 *
 * Sidebar component displaying chat session history.
 *
 * Features:
 * - List of all chat sessions
 * - New chat button
 * - Active session highlight
 * - Session deletion
 * - Loading and empty states
 */

import React, { useState } from 'react';
import { Plus, MessageSquare, Trash2, MoreVertical } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { ChatSession } from '../../types/chat.types';
import { Button } from '../ui/Button';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { ROUTES } from '../../utils/constants';
import { cn } from '../../utils/cn';

/**
 * SessionList Props
 */
interface SessionListProps {
  sessions: ChatSession[];
  activeSessionId?: string | null;
  isLoading?: boolean;
  onNewChat: () => void;
  onDeleteSession?: (sessionId: string) => void;
}

/**
 * SessionItem Component
 */
interface SessionItemProps {
  session: ChatSession;
  isActive: boolean;
  onDelete?: (sessionId: string) => void;
}

const SessionItem: React.FC<SessionItemProps> = ({
  session,
  isActive,
  onDelete,
}) => {
  const navigate = useNavigate();
  const [showMenu, setShowMenu] = useState(false);

  const handleClick = () => {
    navigate(ROUTES.CHAT_SESSION(session.id));
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete && confirm('Delete this chat?')) {
      onDelete(session.id);
    }
    setShowMenu(false);
  };

  const toggleMenu = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowMenu(!showMenu);
  };

  return (
    <div
      onClick={handleClick}
      className={cn(
        'group relative px-3 py-3 rounded-lg cursor-pointer transition-all duration-200',
        'hover:bg-dark-800',
        isActive
          ? 'bg-primary-600/20 border border-primary-500/30'
          : 'border border-transparent'
      )}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div
          className={cn(
            'flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center',
            isActive
              ? 'bg-primary-600 text-white'
              : 'bg-dark-700 text-dark-400 group-hover:bg-dark-600'
          )}
        >
          <MessageSquare size={16} />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h4
            className={cn(
              'text-sm font-medium truncate',
              isActive ? 'text-white' : 'text-dark-200'
            )}
          >
            {session.title || 'New Chat'}
          </h4>
          {session.lastMessage && (
            <p className="text-xs text-dark-500 truncate mt-0.5">
              {session.lastMessage}
            </p>
          )}
          <p className="text-xs text-dark-600 mt-1">
            {new Date(session.updatedAt).toLocaleDateString()}
          </p>
        </div>

        {/* Menu Button */}
        <div className="relative flex-shrink-0">
          <button
            onClick={toggleMenu}
            className={cn(
              'w-6 h-6 rounded flex items-center justify-center',
              'text-dark-500 hover:text-dark-300 hover:bg-dark-700',
              'opacity-0 group-hover:opacity-100 transition-opacity',
              showMenu && 'opacity-100'
            )}
          >
            <MoreVertical size={16} />
          </button>

          {/* Dropdown Menu */}
          {showMenu && (
            <>
              {/* Backdrop */}
              <div
                className="fixed inset-0 z-10"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowMenu(false);
                }}
              />

              {/* Menu */}
              <div className="absolute right-0 top-8 z-20 w-40 bg-dark-800 border border-dark-700 rounded-lg shadow-xl py-1">
                <button
                  onClick={handleDelete}
                  className="w-full px-3 py-2 text-left text-sm text-red-400 hover:bg-dark-700 flex items-center gap-2"
                >
                  <Trash2 size={14} />
                  Delete
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * SessionList Component
 */
export const SessionList: React.FC<SessionListProps> = ({
  sessions,
  activeSessionId,
  isLoading,
  onNewChat,
  onDeleteSession,
}) => {
  return (
    <div className="w-80 bg-dark-900 border-r border-dark-800 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-dark-800">
        <Button
          onClick={onNewChat}
          variant="primary"
          size="md"
          fullWidth
          className="gap-2"
        >
          <Plus size={18} />
          New Chat
        </Button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-dark-700 scrollbar-track-dark-900 p-3">
        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner />
          </div>
        )}

        {/* Empty State */}
        {!isLoading && sessions.length === 0 && (
          <div className="text-center py-8 px-4">
            <MessageSquare size={32} className="mx-auto mb-3 text-dark-600" />
            <p className="text-sm text-dark-500">No chat history yet</p>
            <p className="text-xs text-dark-600 mt-1">
              Start a new conversation
            </p>
          </div>
        )}

        {/* Sessions */}
        {!isLoading && sessions.length > 0 && (
          <div className="space-y-2">
            {sessions.map((session) => (
              <SessionItem
                key={session.id}
                session={session}
                isActive={session.id === activeSessionId}
                onDelete={onDeleteSession}
              />
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-dark-800">
        <div className="text-xs text-dark-600 text-center">
          {sessions.length} {sessions.length === 1 ? 'chat' : 'chats'}
        </div>
      </div>
    </div>
  );
};

