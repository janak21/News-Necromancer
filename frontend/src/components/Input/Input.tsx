import React, { forwardRef } from 'react';
import './Input.css';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  variant?: 'default' | 'ghost';
  fullWidth?: boolean;
}

const Input = forwardRef<HTMLInputElement, InputProps>(({
  label,
  error,
  helperText,
  leftIcon,
  rightIcon,
  variant = 'default',
  fullWidth = false,
  className = '',
  id,
  ...props
}, ref) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
  
  const baseClasses = 'spooky-input';
  const variantClass = `spooky-input--${variant}`;
  const errorClass = error ? 'spooky-input--error' : '';
  const fullWidthClass = fullWidth ? 'spooky-input--full-width' : '';
  const hasIconsClass = (leftIcon || rightIcon) ? 'spooky-input--has-icons' : '';
  
  const wrapperClasses = [
    'spooky-input-wrapper',
    fullWidthClass
  ].filter(Boolean).join(' ');
  
  const inputClasses = [
    baseClasses,
    variantClass,
    errorClass,
    hasIconsClass,
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={wrapperClasses}>
      {label && (
        <label htmlFor={inputId} className="spooky-input__label">
          {label}
        </label>
      )}
      
      <div className="spooky-input__container">
        {leftIcon && (
          <span className="spooky-input__icon spooky-input__icon--left">
            {leftIcon}
          </span>
        )}
        
        <input
          ref={ref}
          id={inputId}
          className={inputClasses}
          {...props}
        />
        
        {rightIcon && (
          <span className="spooky-input__icon spooky-input__icon--right">
            {rightIcon}
          </span>
        )}
      </div>
      
      {(error || helperText) && (
        <div className="spooky-input__feedback">
          {error ? (
            <span className="spooky-input__error">{error}</span>
          ) : (
            <span className="spooky-input__helper">{helperText}</span>
          )}
        </div>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;