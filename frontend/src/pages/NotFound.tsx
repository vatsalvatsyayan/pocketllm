/**
 * 404 Not Found Page
 *
 * Displayed when user navigates to a non-existent route.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { ROUTES } from '../utils/constants';

/**
 * 404 Not Found page
 */
export const NotFound: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-dark flex items-center justify-center p-4">
      <div className="text-center max-w-md">
        {/* 404 illustration */}
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-primary-500/20 mb-4">404</h1>
          <h2 className="text-3xl font-bold text-white mb-2">Page Not Found</h2>
          <p className="text-dark-400">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button
            variant="outline"
            onClick={() => navigate(-1)}
            className="flex items-center gap-2"
          >
            <ArrowLeft size={18} />
            Go Back
          </Button>
          <Button
            variant="primary"
            onClick={() => navigate(ROUTES.CHAT)}
            className="flex items-center gap-2"
          >
            <Home size={18} />
            Go Home
          </Button>
        </div>
      </div>
    </div>
  );
};
