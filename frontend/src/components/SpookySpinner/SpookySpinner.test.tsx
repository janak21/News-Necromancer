import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import SpookySpinner from './SpookySpinner';

describe('SpookySpinner', () => {
  it('renders without message', () => {
    const { container } = render(<SpookySpinner />);
    expect(container.querySelector('.spooky-spinner')).toBeInTheDocument();
  });

  it('displays message when provided', () => {
    render(<SpookySpinner message="Loading spooky content..." />);
    expect(screen.getByText('Loading spooky content...')).toBeInTheDocument();
  });

  it('renders ghost variant by default', () => {
    const { container } = render(<SpookySpinner />);
    expect(container.querySelector('.spooky-spinner__ghost')).toBeInTheDocument();
  });

  it('renders skull variant when specified', () => {
    const { container } = render(<SpookySpinner variant="skull" />);
    expect(container.querySelector('.spooky-spinner__skull')).toBeInTheDocument();
  });

  it('renders spiral variant when specified', () => {
    const { container } = render(<SpookySpinner variant="spiral" />);
    expect(container.querySelector('.spooky-spinner__spiral')).toBeInTheDocument();
  });

  it('applies size classes correctly', () => {
    const { container } = render(<SpookySpinner size="large" />);
    expect(container.querySelector('.spooky-spinner--large')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(<SpookySpinner className="custom-class" />);
    expect(container.querySelector('.custom-class')).toBeInTheDocument();
  });
});
