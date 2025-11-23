/**
 * Admin Dashboard Component
 *
 * Displays system-wide metrics and admin controls.
 * Only accessible to admin users.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Users, 
  MessageSquare, 
  FolderOpen, 
  Clock,
  Shield,
  Activity,
  BarChart3
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { apiClient } from '../services/api/apiClient';
import { ADMIN_ENDPOINTS } from '../services/api/endpoints';
import { ROUTES } from '../utils/constants';
import { logError } from '../utils/errorHandler';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { Alert } from '../components/ui/Alert';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';

interface Metrics {
  overview: {
    total_users: number;
    total_sessions: number;
    total_messages: number;
    admin_count: number;
    active_users: number;
  };
  recent_activity: {
    new_users_24h: number;
    new_sessions_24h: number;
    new_messages_24h: number;
  };
  messages: {
    user_messages: number;
    assistant_messages: number;
    avg_per_session: number;
  };
}

/**
 * Admin Dashboard Component
 */
export const AdminDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  // Redirect if not admin
  useEffect(() => {
    if (user && !user.is_admin) {
      navigate(ROUTES.CHAT);
    }
  }, [user, navigate]);

  // Load metrics
  useEffect(() => {
    loadMetrics();
    // Refresh every 30 seconds
    const interval = setInterval(loadMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadMetrics = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await apiClient.get<Metrics>(ADMIN_ENDPOINTS.METRICS);
      setMetrics(data);
      setLastRefresh(new Date());
    } catch (err) {
      logError(err, 'Load admin metrics');
      setError('Failed to load metrics. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!user || !user.is_admin) {
    return (
      <div className="min-h-screen bg-dark-900 flex items-center justify-center">
        <Alert variant="error" title="Access Denied">
          You must be an admin to access this page.
        </Alert>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-900 text-dark-100">
      {/* Header */}
      <header className="bg-dark-800 border-b border-dark-700 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Shield size={24} className="text-primary-500" />
              Admin Dashboard
            </h1>
            <p className="text-sm text-dark-400 mt-1">
              System metrics and administration
            </p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-dark-400">
              {user.email}
            </span>
            <Button variant="secondary" onClick={() => navigate(ROUTES.CHAT)}>
              Go to Chat
            </Button>
            <Button variant="danger" onClick={logout}>
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Refresh Button */}
        <div className="mb-6 flex items-center justify-between">
          <div className="text-sm text-dark-400">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </div>
          <Button variant="secondary" onClick={loadMetrics} disabled={isLoading}>
            {isLoading ? 'Refreshing...' : 'Refresh'}
          </Button>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="error" title="Error" onClose={() => setError(null)} className="mb-6">
            {error}
          </Alert>
        )}

        {/* Loading State */}
        {isLoading && !metrics && (
          <div className="flex items-center justify-center py-20">
            <LoadingSpinner size="lg" />
          </div>
        )}

        {/* Metrics Grid */}
        {metrics && (
          <div className="space-y-6">
            {/* Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <Card variant="default" padding="md">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-dark-400 mb-1">Total Users</p>
                    <p className="text-3xl font-bold text-white">{metrics.overview.total_users}</p>
                  </div>
                  <Users size={32} className="text-primary-500" />
                </div>
              </Card>

              <Card variant="default" padding="md">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-dark-400 mb-1">Total Sessions</p>
                    <p className="text-3xl font-bold text-white">{metrics.overview.total_sessions}</p>
                  </div>
                  <FolderOpen size={32} className="text-primary-500" />
                </div>
              </Card>

              <Card variant="default" padding="md">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-dark-400 mb-1">Total Messages</p>
                    <p className="text-3xl font-bold text-white">{metrics.overview.total_messages}</p>
                  </div>
                  <MessageSquare size={32} className="text-primary-500" />
                </div>
              </Card>

              <Card variant="default" padding="md">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-dark-400 mb-1">Admins</p>
                    <p className="text-3xl font-bold text-white">{metrics.overview.admin_count}</p>
                  </div>
                  <Shield size={32} className="text-primary-500" />
                </div>
              </Card>

              <Card variant="default" padding="md">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-dark-400 mb-1">Active Users</p>
                    <p className="text-3xl font-bold text-white">{metrics.overview.active_users}</p>
                  </div>
                  <Activity size={32} className="text-primary-500" />
                </div>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card variant="default" padding="lg">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Clock size={20} />
                Recent Activity (24h)
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-dark-800 rounded-lg p-4">
                  <p className="text-sm text-dark-400 mb-1">New Users</p>
                  <p className="text-2xl font-bold text-white">{metrics.recent_activity.new_users_24h}</p>
                </div>
                <div className="bg-dark-800 rounded-lg p-4">
                  <p className="text-sm text-dark-400 mb-1">New Sessions</p>
                  <p className="text-2xl font-bold text-white">{metrics.recent_activity.new_sessions_24h}</p>
                </div>
                <div className="bg-dark-800 rounded-lg p-4">
                  <p className="text-sm text-dark-400 mb-1">New Messages</p>
                  <p className="text-2xl font-bold text-white">{metrics.recent_activity.new_messages_24h}</p>
                </div>
              </div>
            </Card>

            {/* Message Statistics */}
            <Card variant="default" padding="lg">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <BarChart3 size={20} />
                Message Statistics
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-dark-800 rounded-lg p-4">
                  <p className="text-sm text-dark-400 mb-1">User Messages</p>
                  <p className="text-2xl font-bold text-white">{metrics.messages.user_messages}</p>
                </div>
                <div className="bg-dark-800 rounded-lg p-4">
                  <p className="text-sm text-dark-400 mb-1">Assistant Messages</p>
                  <p className="text-2xl font-bold text-white">{metrics.messages.assistant_messages}</p>
                </div>
                <div className="bg-dark-800 rounded-lg p-4">
                  <p className="text-sm text-dark-400 mb-1">Avg per Session</p>
                  <p className="text-2xl font-bold text-white">{metrics.messages.avg_per_session}</p>
                </div>
              </div>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
};

