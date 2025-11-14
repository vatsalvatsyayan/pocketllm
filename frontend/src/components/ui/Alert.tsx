/**
 * Alert Component
 *
 * Displays informational, success, warning, or error messages.
 * Used for form feedback and notifications.
 */

import React from 'react';
import { AlertCircle, CheckCircle, Info, XCircle } from 'lucide-react';
import { cn } from '../../utils/cn';

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  children: React.ReactNode;
  onClose?: () => void;
}

/**
 * Alert component for displaying messages
 */
export const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  ({ variant = 'info', title, children, onClose, className, ...props }, ref) => {
    // Variant configurations
    const variants = {
      info: {
        container: 'bg-blue-500/10 border-blue-500/50 text-blue-300',
        icon: Info,
        iconColor: 'text-blue-400',
      },
      success: {
        container: 'bg-green-500/10 border-green-500/50 text-green-300',
        icon: CheckCircle,
        iconColor: 'text-green-400',
      },
      warning: {
        container: 'bg-yellow-500/10 border-yellow-500/50 text-yellow-300',
        icon: AlertCircle,
        iconColor: 'text-yellow-400',
      },
      error: {
        container: 'bg-red-500/10 border-red-500/50 text-red-300',
        icon: XCircle,
        iconColor: 'text-red-400',
      },
    };

    const config = variants[variant];
    const Icon = config.icon;

    return (
      <div
        ref={ref}
        role="alert"
        className={cn(
          'relative rounded-lg border p-4 flex gap-3',
          config.container,
          className
        )}
        {...props}
      >
        {/* Icon */}
        <Icon className={cn('h-5 w-5 flex-shrink-0 mt-0.5', config.iconColor)} />

        {/* Content */}
        <div className="flex-1">
          {title && <h5 className="font-semibold mb-1">{title}</h5>}
          <div className="text-sm">{children}</div>
        </div>

        {/* Close button */}
        {onClose && (
          <button
            onClick={onClose}
            className="flex-shrink-0 ml-auto hover:opacity-70 transition-opacity"
            aria-label="Close alert"
          >
            <XCircle className="h-4 w-4" />
          </button>
        )}
      </div>
    );
  }
);

Alert.displayName = 'Alert';
