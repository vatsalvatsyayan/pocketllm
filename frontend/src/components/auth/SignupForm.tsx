/**
 * Signup Form Component
 *
 * Handles new user registration.
 * Includes validation, error handling, and loading states.
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Alert } from '../ui/Alert';
import { validateSignupForm } from '../../utils/validation';
import { ROUTES } from '../../utils/constants';

/**
 * Signup form component
 */
export const SignupForm: React.FC = () => {
  const navigate = useNavigate();
  const { signup } = useAuth();

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState<{
    name?: string;
    email?: string;
    password?: string;
    confirmPassword?: string;
  }>({});
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  /**
   * Handles input change
   */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setErrors((prev) => ({ ...prev, [name]: undefined }));
  };

  /**
   * Validates form fields
   */
  const validateForm = (): boolean => {
    const validation = validateSignupForm(
      formData.name,
      formData.email,
      formData.password,
      formData.confirmPassword
    );

    const newErrors: any = {};
    if (!validation.name.isValid) newErrors.name = validation.name.error;
    if (!validation.email.isValid) newErrors.email = validation.email.error;
    if (!validation.password.isValid) newErrors.password = validation.password.error;
    if (!validation.confirmPassword.isValid)
      newErrors.confirmPassword = validation.confirmPassword.error;

    setErrors(newErrors);
    return validation.isValid;
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
      await signup({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        confirmPassword: formData.confirmPassword,
      });

      // Navigate to dashboard after successful signup
      navigate(ROUTES.DASHBOARD, { replace: true });
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : 'Signup failed. Please try again.'
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

      {/* Name Input */}
      <Input
        type="text"
        name="name"
        label="Full Name"
        placeholder="John Doe"
        value={formData.name}
        onChange={handleChange}
        error={errors.name}
        icon={<User size={20} />}
        required
        fullWidth
        autoComplete="name"
      />

      {/* Email Input */}
      <Input
        type="email"
        name="email"
        label="Email"
        placeholder="your@email.com"
        value={formData.email}
        onChange={handleChange}
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
        value={formData.password}
        onChange={handleChange}
        error={errors.password}
        icon={<Lock size={20} />}
        helperText="At least 6 characters with uppercase, lowercase, and number"
        required
        fullWidth
        autoComplete="new-password"
      />

      {/* Confirm Password Input */}
      <Input
        type="password"
        name="confirmPassword"
        label="Confirm Password"
        placeholder="••••••••"
        value={formData.confirmPassword}
        onChange={handleChange}
        error={errors.confirmPassword}
        icon={<Lock size={20} />}
        required
        fullWidth
        autoComplete="new-password"
      />

      {/* Submit Button */}
      <Button
        type="submit"
        variant="primary"
        size="lg"
        fullWidth
        isLoading={isLoading}
      >
        {isLoading ? 'Creating account...' : 'Create Account'}
      </Button>

      {/* Login Link */}
      <p className="text-center text-sm text-dark-400">
        Already have an account?{' '}
        <Link
          to={ROUTES.LOGIN}
          className="text-primary-400 hover:text-primary-300 font-medium transition-colors"
        >
          Sign in
        </Link>
      </p>
    </form>
  );
};
