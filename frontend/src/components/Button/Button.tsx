import React from 'react';
import './Button.css';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  fullWidth = false,
  className = '',
  disabled,
  ...props
}) => {
  const baseClasses = 'spooky-button';
  const variantClass = `spooky-button--${variant}`;
  const sizeClass = `spooky-button--${size}`;
  const fullWidthClass = fullWidth ? 'spooky-button--full-width' : '';
  const loadingClass = isLoading ? 'spooky-button--loading' : '';
  
  const classes = [
    baseClasses,
    variantClass,
    sizeClass,
    fullWidthClass,
    loadingClass,
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      className={classes}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && (
        <span className="spooky-button__spinner" aria-hidden="true">
          <svg className="spooky-button__spinner-icon" viewBox="0 0 24 24">
            <circle
              className="spooky-button__spinner-circle"
              cx="12"
              cy="12"
              r="10"
              fill="none"
              strokeWidth="2"
            />
          </svg>
        </span>
      )}
      
      {!isLoading && leftIcon && (
        <span className="spooky-button__icon spooky-button__icon--left">
          {leftIcon}
        </span>
      )}
      
      <span className="spooky-button__content">
        {children}
      </span>
      
      {!isLoading && rightIcon && (
        <span className="spooky-button__icon spooky-button__icon--right">
          {rightIcon}
        </span>
      )}
    </button>
  );
};

export default Button;