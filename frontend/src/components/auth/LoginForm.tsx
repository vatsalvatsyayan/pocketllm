/**
 * Login Form Component
 *
 * Handles user login with email and password.
 * Includes validation, error handling, and loading states.
 */

import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Mail, Lock } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Alert } from '../ui/Alert';
import { validateEmail, validatePassword } from '../../utils/validation';
import { ROUTES } from '../../utils/constants';

/**
 * Login form component
 */
export const LoginForm: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  // Form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  /**
   * Validates form fields
   */
  const validateForm = (): boolean => {
    const newErrors: { email?: string; password?: string } = {};

    const emailValidation = validateEmail(email);
    if (!emailValidation.isValid) {
      newErrors.email = emailValidation.error;
    }

    const passwordValidation = validatePassword(password, false);
    if (!passwordValidation.isValid) {
      newErrors.password = passwordValidation.error;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handles form submission
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    // Validate
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      await login({ email, password, rememberMe });

      // Get the page they tried to visit before login, or default to chat
      const from = (location.state as any)?.from?.pathname || ROUTES.CHAT;
      navigate(from, { replace: true });
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : 'Login failed. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Error Alert */}
      {errorMessage && (
        <Alert variant="error" onClose={() => setErrorMessage(null)}>
          {errorMessage}
        </Alert>
      )}

      {/* Demo Credentials Info */}
      <Alert variant="info">
        <strong>Demo Credentials: (Admin User)</strong>
        <br />
        Email: demo@pocketllm.com
        <br />
        Password: demo123
      </Alert>

      {/* Email Input */}
      <Input
        type="email"
        name="email"
        label="Email"
        placeholder="your@email.com"
        value={email}
        onChange={(e) => {
          setEmail(e.target.value);
          setErrors((prev) => ({ ...prev, email: undefined }));
        }}
        error={errors.email}
        icon={<Mail size={20} />}
        required
        fullWidth
        autoComplete="email"
      />

      {/* Password Input */}
      <Input
        type="password"
        name="password"
        label="Password"
        placeholder="••••••••"
        value={password}
        onChange={(e) => {
          setPassword(e.target.value);
          setErrors((prev) => ({ ...prev, password: undefined }));
        }}
        error={errors.password}
        icon={<Lock size={20} />}
        required
        fullWidth
        autoComplete="current-password"
      />

      {/* Remember Me & Forgot Password */}
      <div className="flex items-center justify-between text-sm">
        <label className="flex items-center gap-2 cursor-pointer text-dark-300">
          <input
            type="checkbox"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
            className="w-4 h-4 rounded border-dark-600 bg-dark-700 text-primary-600 focus:ring-2 focus:ring-primary-500 focus:ring-offset-dark-900"
          />
          Remember me
        </label>

        <a
          href="#"
          className="text-primary-400 hover:text-primary-300 transition-colors"
        >
          Forgot password?
        </a>
      </div>

      {/* Submit Button */}
      <Button
        type="submit"
        variant="primary"
        size="lg"
        fullWidth
        isLoading={isLoading}
      >
        {isLoading ? 'Signing in...' : 'Sign In'}
      </Button>

      {/* Sign Up Link */}
      <p className="text-center text-sm text-dark-400">
        Don't have an account?{' '}
        <Link
          to={ROUTES.SIGNUP}
          className="text-primary-400 hover:text-primary-300 font-medium transition-colors"
        >
          Sign up
        </Link>
      </p>
    </form>
  );
};
