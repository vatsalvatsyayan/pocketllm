/**
 * Signup Page
 *
 * New user registration page.
 */

import React from 'react';
import { AuthLayout } from '../components/layout/AuthLayout';
import { SignupForm } from '../components/auth/SignupForm';

/**
 * Signup page component
 */
export const Signup: React.FC = () => {
  return (
    <AuthLayout
      title="Create an account"
      subtitle="Get started with pocketLLM in seconds"
    >
      <SignupForm />
    </AuthLayout>
  );
};
