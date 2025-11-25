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

  it('handles text with missing spaces between words', () => {
    const malformedText = 'ThegroupsformedonAmazonMusicandSpotifyareexcellent';
    const { container } = render(
      <SupernaturalReveal explanation={malformedText} isExpanded={true} />
    );
    
    const content = container.querySelector('.supernatural-reveal__text');
    expect(content?.textContent).toContain('Amazon Music');
    expect(content?.textContent).toContain('Spotify');
  });

  it('formats multiple paragraphs with proper spacing', () => {
    const multiParagraph = 'First paragraph here.\n\nSecond paragraph here.\n\nThird paragraph here.';
    const { container } = render(
      <SupernaturalReveal explanation={multiParagraph} isExpanded={true} />
    );
    
    const paragraphs = container.querySelectorAll('.supernatural-reveal__paragraph');
    expect(paragraphs.length).toBe(3);
    expect(paragraphs[0].textContent).toContain('First paragraph');
    expect(paragraphs[1].textContent).toContain('Second paragraph');
    expect(paragraphs[2].textContent).toContain('Third paragraph');
  });

  it('handles single paragraph with word-by-word animation', () => {
    const singleParagraph = 'This is a single paragraph without breaks';
    const { container } = render(
      <SupernaturalReveal explanation={singleParagraph} isExpanded={true} />
    );
    
    const words = container.querySelectorAll('.supernatural-reveal__word');
    expect(words.length).toBeGreaterThan(0);
  });
});
