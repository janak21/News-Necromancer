import React from 'react';
import './Layout.css';

export interface LayoutProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'container' | 'full' | 'centered';
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const Layout: React.FC<LayoutProps> = ({
  children,
  variant = 'container',
  maxWidth = 'xl',
  padding = 'md',
  className = '',
  ...props
}) => {
  const baseClasses = 'spooky-layout';
  const variantClass = `spooky-layout--${variant}`;
  const maxWidthClass = `spooky-layout--max-${maxWidth}`;
  const paddingClass = `spooky-layout--padding-${padding}`;
  
  const classes = [
    baseClasses,
    variantClass,
    maxWidthClass,
    paddingClass,
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};

// Grid Component
export interface GridProps extends React.HTMLAttributes<HTMLDivElement> {
  cols?: 1 | 2 | 3 | 4 | 6 | 12;
  gap?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  responsive?: boolean;
}

export const Grid: React.FC<GridProps> = ({
  children,
  cols = 1,
  gap = 'md',
  responsive = true,
  className = '',
  ...props
}) => {
  const baseClasses = 'spooky-grid';
  const colsClass = `spooky-grid--cols-${cols}`;
  const gapClass = `spooky-grid--gap-${gap}`;
  const responsiveClass = responsive ? 'spooky-grid--responsive' : '';
  
  const classes = [
    baseClasses,
    colsClass,
    gapClass,
    responsiveClass,
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};

// Flex Component
export interface FlexProps extends React.HTMLAttributes<HTMLDivElement> {
  direction?: 'row' | 'column';
  align?: 'start' | 'center' | 'end' | 'stretch';
  justify?: 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly';
  wrap?: boolean;
  gap?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
}

export const Flex: React.FC<FlexProps> = ({
  children,
  direction = 'row',
  align = 'start',
  justify = 'start',
  wrap = false,
  gap = 'none',
  className = '',
  ...props
}) => {
  const baseClasses = 'spooky-flex';
  const directionClass = `spooky-flex--${direction}`;
  const alignClass = `spooky-flex--align-${align}`;
  const justifyClass = `spooky-flex--justify-${justify}`;
  const wrapClass = wrap ? 'spooky-flex--wrap' : '';
  const gapClass = gap !== 'none' ? `spooky-flex--gap-${gap}` : '';
  
  const classes = [
    baseClasses,
    directionClass,
    alignClass,
    justifyClass,
    wrapClass,
    gapClass,
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};

export default Layout;