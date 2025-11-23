/**
 * User Type Definitions
 *
 * Defines the structure of user objects throughout the application.
 * These types ensure type safety when working with user data.
 */

export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: string;
  // Add additional user properties as needed
  is_admin?: boolean;
  avatar?: string;
}

export interface UserProfile extends User {
  // Extended user information for profile pages
  bio?: string;
  preferences?: UserPreferences;
}

export interface UserPreferences {
  theme?: 'light' | 'dark' | 'auto';
  language?: string;
  notifications?: boolean;
}
