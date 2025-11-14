/**
 * Validation Utilities
 *
 * Centralized validation logic for forms and inputs.
 * Follows DRY principle by consolidating all validation rules.
 */

import { VALIDATION, ERROR_MESSAGES } from './constants';

/**
 * Validation result type
 */
export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * Validates email format
 */
export const validateEmail = (email: string): ValidationResult => {
  if (!email || email.trim() === '') {
    return { isValid: false, error: ERROR_MESSAGES.EMAIL_REQUIRED };
  }

  if (email.length < VALIDATION.EMAIL.MIN_LENGTH) {
    return { isValid: false, error: ERROR_MESSAGES.EMAIL_INVALID };
  }

  if (!VALIDATION.EMAIL.PATTERN.test(email)) {
    return { isValid: false, error: ERROR_MESSAGES.EMAIL_INVALID };
  }

  return { isValid: true };
};

/**
 * Validates password strength
 */
export const validatePassword = (password: string, requireStrong: boolean = VALIDATION.PASSWORD.REQUIRE_STRONG): ValidationResult => {
  if (!password || password.trim() === '') {
    return { isValid: false, error: ERROR_MESSAGES.PASSWORD_REQUIRED };
  }

  if (password.length < VALIDATION.PASSWORD.MIN_LENGTH) {
    return { isValid: false, error: ERROR_MESSAGES.PASSWORD_TOO_SHORT };
  }

  if (password.length > VALIDATION.PASSWORD.MAX_LENGTH) {
    return { isValid: false, error: 'Password is too long.' };
  }

  if (requireStrong && !VALIDATION.PASSWORD.PATTERN.test(password)) {
    return { isValid: false, error: ERROR_MESSAGES.PASSWORD_TOO_WEAK };
  }

  return { isValid: true };
};

/**
 * Validates password confirmation
 */
export const validatePasswordMatch = (password: string, confirmPassword: string): ValidationResult => {
  if (password !== confirmPassword) {
    return { isValid: false, error: ERROR_MESSAGES.PASSWORDS_DONT_MATCH };
  }

  return { isValid: true };
};

/**
 * Validates name
 */
export const validateName = (name: string): ValidationResult => {
  if (!name || name.trim() === '') {
    return { isValid: false, error: ERROR_MESSAGES.NAME_REQUIRED };
  }

  if (name.length < VALIDATION.NAME.MIN_LENGTH) {
    return { isValid: false, error: ERROR_MESSAGES.NAME_TOO_SHORT };
  }

  if (name.length > VALIDATION.NAME.MAX_LENGTH) {
    return { isValid: false, error: 'Name is too long.' };
  }

  return { isValid: true };
};

/**
 * Validates login form
 */
export const validateLoginForm = (email: string, password: string) => {
  const emailValidation = validateEmail(email);
  const passwordValidation = validatePassword(password, false); // Don't require strong password for login

  return {
    email: emailValidation,
    password: passwordValidation,
    isValid: emailValidation.isValid && passwordValidation.isValid,
  };
};

/**
 * Validates signup form
 */
export const validateSignupForm = (name: string, email: string, password: string, confirmPassword: string) => {
  const nameValidation = validateName(name);
  const emailValidation = validateEmail(email);
  const passwordValidation = validatePassword(password, true); // Require strong password for signup
  const passwordMatchValidation = validatePasswordMatch(password, confirmPassword);

  return {
    name: nameValidation,
    email: emailValidation,
    password: passwordValidation,
    confirmPassword: passwordMatchValidation,
    isValid:
      nameValidation.isValid &&
      emailValidation.isValid &&
      passwordValidation.isValid &&
      passwordMatchValidation.isValid,
  };
};
