/**
 * Class Name Utility
 *
 * Combines clsx and tailwind-merge for better Tailwind class handling.
 * Prevents style conflicts when merging Tailwind classes.
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merges Tailwind CSS classes without conflicts
 * @param inputs - Class names or conditional class objects
 * @returns Merged class string
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
