/**
 * Login Page
 *
 * User login page with authentication form.
 */

import React from 'react';
import { AuthLayout } from '../components/layout/AuthLayout';
import { LoginForm } from '../components/auth/LoginForm';

/**
 * Login page component
 */
export const Login: React.FC = () => {
  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to your pocketLLM account"
    >
      <LoginForm />
    </AuthLayout>
  );
};
