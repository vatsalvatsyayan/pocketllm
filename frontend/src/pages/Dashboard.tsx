/**
 * Dashboard Page
 *
 * Main dashboard for authenticated users.
 * This is a placeholder - will be extended with LLM chat functionality.
 */

import React from 'react';
import { MessageSquare, Sparkles, Zap, Shield } from 'lucide-react';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { useAuth } from '../hooks/useAuth';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';

/**
 * Dashboard page component
 */
export const Dashboard: React.FC = () => {
  const { user } = useAuth();

  const features = [
    {
      icon: MessageSquare,
      title: 'Chat Interface',
      description: 'Interactive chat with local language models',
      color: 'text-primary-400',
    },
    {
      icon: Sparkles,
      title: 'Multiple Models',
      description: 'Support for various small language models',
      color: 'text-accent-400',
    },
    {
      icon: Zap,
      title: 'Fast & Local',
      description: 'All processing happens on your machine',
      color: 'text-yellow-400',
    },
    {
      icon: Shield,
      title: 'Privacy First',
      description: 'Your data never leaves your device',
      color: 'text-green-400',
    },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Welcome section */}
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">
            Welcome back, {user?.name}!
          </h1>
          <p className="text-dark-400 text-lg">
            Your pocketLLM portal is ready to use.
          </p>
        </div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card key={index} variant="glass" padding="lg">
                <div className="flex items-start gap-4">
                  <div className={`${feature.color}`}>
                    <Icon size={32} />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-1">
                      {feature.title}
                    </h3>
                    <p className="text-dark-400">{feature.description}</p>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Coming soon section */}
        <Card variant="elevated" padding="lg">
          <CardHeader>
            <CardTitle>Coming Soon</CardTitle>
            <CardDescription>
              The LLM chat interface is under development
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-dark-700/50 rounded-lg p-6 border-2 border-dashed border-dark-600">
              <div className="text-center">
                <MessageSquare size={48} className="mx-auto mb-4 text-dark-500" />
                <h4 className="text-lg font-semibold text-dark-300 mb-2">
                  Chat Interface
                </h4>
                <p className="text-dark-500 text-sm">
                  The interactive chat interface will be available soon.
                  <br />
                  Stay tuned for updates!
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* User info card */}
        <Card variant="glass" padding="lg">
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-dark-400">Email:</span>
                <span className="text-white font-medium">{user?.email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-dark-400">Account Type:</span>
                <span className="text-white font-medium capitalize">
                  {user?.is_admin ? 'Admin' : 'User'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-dark-400">Member Since:</span>
                <span className="text-white font-medium">
                  {user?.createdAt
                    ? new Date(user.createdAt).toLocaleDateString()
                    : 'N/A'}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};
