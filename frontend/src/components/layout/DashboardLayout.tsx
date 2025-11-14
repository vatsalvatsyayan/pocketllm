/**
 * Dashboard Layout Component
 *
 * Layout wrapper for authenticated pages.
 * Includes navigation, header, and logout functionality.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Cpu, LogOut, User } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../ui/Button';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

/**
 * Dashboard layout with navigation
 */
export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-dark">
      {/* Header */}
      <header className="bg-dark-800/50 backdrop-blur-xl border-b border-dark-700/50 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-primary-600 to-accent-600 rounded-lg shadow-lg shadow-primary-500/50">
                <Cpu size={20} className="text-white" />
              </div>
              <h1 className="text-xl font-bold text-white">
                pocket<span className="text-primary-400">LLM</span>
              </h1>
            </div>

            {/* User menu */}
            <div className="flex items-center gap-4">
              {/* User info */}
              <div className="flex items-center gap-2 text-dark-300">
                <User size={18} />
                <span className="text-sm font-medium">{user?.name}</span>
              </div>

              {/* Logout button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                className="flex items-center gap-2"
              >
                <LogOut size={16} />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
};
