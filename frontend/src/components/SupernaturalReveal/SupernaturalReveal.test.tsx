import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import SupernaturalReveal from './SupernaturalReveal';

describe('SupernaturalReveal', () => {
  const mockExplanation = 'A dark force haunts this place';

  it('renders the trigger button', () => {
    render(<SupernaturalReveal explanation={mockExplanation} />);
    expect(screen.getByText('Supernatural Explanation')).toBeInTheDocument();
  });

  it('toggles expansion when clicked', () => {
    const { container } = render(<SupernaturalReveal explanation={mockExplanation} />);
    const button = screen.getByRole('button');
    
    fireEvent.click(button);
    const content = container.querySelector('.supernatural-reveal__text');
    expect(content).toBeInTheDocument();
    expect(content?.textContent).toContain('dark force');
  });

  it('calls onToggle callback when provided', () => {
    const onToggle = vi.fn();
    render(<SupernaturalReveal explanation={mockExplanation} onToggle={onToggle} />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(onToggle).toHaveBeenCalledWith(true);
  });

  it('respects controlled expansion state', () => {
    const { rerender, container } = render(
      <SupernaturalReveal explanation={mockExplanation} isExpanded={false} />
    );
    
    expect(container.querySelector('.supernatural-reveal__text')).not.toBeInTheDocument();
    
    rerender(<SupernaturalReveal explanation={mockExplanation} isExpanded={true} />);
    const content = container.querySelector('.supernatural-reveal__text');
    expect(content).toBeInTheDocument();
    expect(content?.textContent).toContain('dark force');
  });
});
