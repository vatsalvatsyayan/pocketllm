/**
 * Auth Layout Component
 *
 * Layout wrapper for authentication pages (login, signup).
 * Provides consistent styling and structure with pocketLLM branding.
 */

import React from 'react';
import { Cpu } from 'lucide-react';

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  subtitle: string;
}

/**
 * Authentication pages layout
 */
export const AuthLayout: React.FC<AuthLayoutProps> = ({
  children,
  title,
  subtitle,
}) => {
  return (
    <div className="min-h-screen bg-gradient-dark flex items-center justify-center p-4">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent-500/10 rounded-full blur-3xl" />
      </div>

      {/* Main content */}
      <div className="relative w-full max-w-md">
        {/* Logo and branding */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-600 to-accent-600 rounded-2xl mb-4 shadow-lg shadow-primary-500/50">
            <Cpu size={32} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">
            pocket<span className="text-primary-400">LLM</span>
          </h1>
          <p className="text-dark-400 text-sm">
            Chat with local small language models
          </p>
        </div>

        {/* Auth card */}
        <div className="bg-dark-800/40 backdrop-blur-xl border border-dark-700/50 rounded-2xl shadow-2xl p-8">
          {/* Title and subtitle */}
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-white mb-2">{title}</h2>
            <p className="text-dark-400 text-sm">{subtitle}</p>
          </div>

          {/* Form content */}
          {children}
        </div>

        {/* Footer */}
        <p className="text-center text-dark-500 text-xs mt-6">
          © 2025 pocketLLM Portal. Built with React + TypeScript.
        </p>
      </div>
    </div>
  );
};
