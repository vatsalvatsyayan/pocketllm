/**
 * Card Component
 *
 * Container component with glassmorphism effect.
 * Used for login/signup forms and content sections.
 */

import React from 'react';
import { cn } from '../../utils/cn';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glass' | 'elevated';
  padding?: 'sm' | 'md' | 'lg' | 'none';
  children: React.ReactNode;
}

/**
 * Card container component
 */
export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ variant = 'default', padding = 'md', className, children, ...props }, ref) => {
    // Base styles
    const baseStyles = 'rounded-xl transition-all duration-200';

    // Variant styles
    const variantStyles = {
      default: 'bg-dark-800 border border-dark-700',
      glass:
        'bg-dark-800/40 backdrop-blur-xl border border-dark-700/50 shadow-2xl',
      elevated:
        'bg-dark-800 border border-dark-700 shadow-2xl shadow-dark-900/50',
    };

    // Padding styles
    const paddingStyles = {
      none: '',
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
    };

    return (
      <div
        ref={ref}
        className={cn(
          baseStyles,
          variantStyles[variant],
          paddingStyles[padding],
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

/**
 * Card Header
 */
export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  children,
  ...props
}) => {
  return (
    <div className={cn('mb-4', className)} {...props}>
      {children}
    </div>
  );
};

/**
 * Card Title
 */
export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({
  className,
  children,
  ...props
}) => {
  return (
    <h2
      className={cn('text-2xl font-bold text-dark-50', className)}
      {...props}
    >
      {children}
    </h2>
  );
};

/**
 * Card Description
 */
export const CardDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({
  className,
  children,
  ...props
}) => {
  return (
    <p className={cn('text-dark-400 mt-1', className)} {...props}>
      {children}
    </p>
  );
};

/**
 * Card Content
 */
export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  children,
  ...props
}) => {
  return (
    <div className={cn('', className)} {...props}>
      {children}
    </div>
  );
};

/**
 * Card Footer
 */
export const CardFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  children,
  ...props
}) => {
  return (
    <div className={cn('mt-6 flex items-center gap-2', className)} {...props}>
      {children}
    </div>
  );
};
