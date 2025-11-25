import React, { useState } from 'react';
import './Button.css';

export interface ButtonProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'onClick'> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void | Promise<void>;
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
  onClick,
  ...props
}) => {
  const [isProcessing, setIsProcessing] = useState(false);

  const handleClick = async (event: React.MouseEvent<HTMLButtonElement>) => {
    if (!onClick || isProcessing || disabled || isLoading) return;

    const result = onClick(event);
    
    // Check if onClick returns a Promise
    if (result instanceof Promise) {
      setIsProcessing(true);
      try {
        await result;
      } catch (error) {
        console.error('Button onClick error:', error);
      } finally {
        setIsProcessing(false);
      }
    }
  };

  const isButtonLoading = isLoading || isProcessing;
  const baseClasses = 'spooky-button';
  const variantClass = `spooky-button--${variant}`;
  const sizeClass = `spooky-button--${size}`;
  const fullWidthClass = fullWidth ? 'spooky-button--full-width' : '';
  const loadingClass = isButtonLoading ? 'spooky-button--loading' : '';
  
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
      disabled={disabled || isButtonLoading}
      onClick={handleClick}
      aria-busy={isButtonLoading}
      {...props}
    >
      {isButtonLoading && (
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
      
      {!isButtonLoading && leftIcon && (
        <span className="spooky-button__icon spooky-button__icon--left">
          {leftIcon}
        </span>
      )}
      
      <span className="spooky-button__content">
        {children}
      </span>
      
      {!isButtonLoading && rightIcon && (
        <span className="spooky-button__icon spooky-button__icon--right">
          {rightIcon}
        </span>
      )}
    </button>
  );
};

export default Button;