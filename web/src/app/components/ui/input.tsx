import * as React from 'react';
import { cn } from './utils';

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, leftIcon, rightIcon, ...props }, ref) => {
    const hasLeftIcon = Boolean(leftIcon);
    const hasRightIcon = Boolean(rightIcon);

    return (
      <div className="relative w-full">
        {hasLeftIcon && (
          <div className="form-control-icon-left">
            {leftIcon}
          </div>
        )}

        <input
          ref={ref}
          type={type}
          data-slot="input"
          className={cn(
            'form-control',
            'file:text-foreground',
            'placeholder:text-muted-foreground',
            'selection:bg-primary selection:text-primary-foreground',
            'aria-invalid:form-control--error',

            hasLeftIcon && 'form-control--icon-left',
            hasRightIcon && 'form-control--icon-right',

            className
          )}
          {...props}
        />

        {hasRightIcon && (
          <div className="form-control-icon-right">
            {rightIcon}
          </div>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };