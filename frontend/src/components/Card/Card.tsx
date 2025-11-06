import React from 'react';
import './Card.css';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined' | 'ghost';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
  glow?: boolean;
}

const Card: React.FC<CardProps> = ({
  children,
  variant = 'default',
  padding = 'md',
  hover = false,
  glow = false,
  className = '',
  ...props
}) => {
  const baseClasses = 'spooky-card';
  const variantClass = `spooky-card--${variant}`;
  const paddingClass = `spooky-card--padding-${padding}`;
  const hoverClass = hover ? 'spooky-card--hover' : '';
  const glowClass = glow ? 'spooky-card--glow' : '';
  
  const classes = [
    baseClasses,
    variantClass,
    paddingClass,
    hoverClass,
    glowClass,
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};

export default Card;