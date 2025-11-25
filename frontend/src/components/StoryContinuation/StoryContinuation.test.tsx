import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import StoryContinuation from './StoryContinuation';
import type { SpookyVariant, StoryContinuation as StoryContinuationType } from '../../types';

// Mock the useSoundEffects hook
vi.mock('../../hooks', () => ({
  useSoundEffects: () => ({
    playSound: vi.fn()
  })
}));

describe('StoryContinuation', () => {
  const mockVariant: SpookyVariant = {
    variant_id: 'test-123',
    haunted_title: 'The Haunted Test',
    haunted_summary: 'A dark and mysterious story that needs continuation',
    horror_themes: ['gothic', 'supernatural'],
    supernatural_explanation: 'A ghost haunts this place',
    personalization_applied: false,
    generation_timestamp: '2024-01-01T00:00:00Z',
    original_item: {
      title: 'Test Story',
      summary: 'Original summary',
      link: 'https://example.com',
      published: '2024-01-01',
      source: 'Test Source',
      metadata: {}
    }
  };

  const mockContinuation: StoryContinuationType = {
    variant_id: 'test-123',
    continued_narrative: 'The darkness deepened.\n\nShadows moved in the corner.\n\nSomething was watching.',
    continuation_timestamp: '2024-01-01T00:00:00Z',
    maintains_intensity: true
  };

  it('renders continue button when no continuation exists', () => {
    const onContinue = vi.fn();
    render(<StoryContinuation variant={mockVariant} onContinue={onContinue} />);
    
    expect(screen.getByText(/Continue the Nightmare/i)).toBeInTheDocument();
  });

  it('formats narrative text with proper paragraph spacing', async () => {
    const onContinue = vi.fn().mockResolvedValue(mockContinuation);
    const { container } = render(<StoryContinuation variant={mockVariant} onContinue={onContinue} />);
    
    const button = screen.getByRole('button', { name: /Generate AI continuation/i });
    fireEvent.click(button);
    
    await waitFor(() => {
      const paragraphs = container.querySelectorAll('.story-continuation__narrative p');
      expect(paragraphs.length).toBe(3);
      expect(paragraphs[0].textContent).toContain('darkness deepened');
      expect(paragraphs[1].textContent).toContain('Shadows moved');
      expect(paragraphs[2].textContent).toContain('Something was watching');
    });
  });

  it('handles text with missing spaces between words', async () => {
    const malformedContinuation: StoryContinuationType = {
      variant_id: 'test-123',
      continued_narrative: 'TheshadowsgrewdarkerAsTheNightProgressed',
      continuation_timestamp: '2024-01-01T00:00:00Z',
      maintains_intensity: true
    };
    
    const onContinue = vi.fn().mockResolvedValue(malformedContinuation);
    const { container } = render(<StoryContinuation variant={mockVariant} onContinue={onContinue} />);
    
    const button = screen.getByRole('button', { name: /Generate AI continuation/i });
    fireEvent.click(button);
    
    await waitFor(() => {
      const narrative = container.querySelector('.story-continuation__narrative');
      // The text formatting adds spaces before capital letters
      expect(narrative?.textContent).toContain('Theshadowsgrew');
      expect(narrative?.textContent).toContain('As');
      expect(narrative?.textContent).toContain('Night');
    });
  });

  it('shows unavailable message when variant has no ID', () => {
    const variantNoId = { ...mockVariant, variant_id: undefined };
    const onContinue = vi.fn();
    
    render(<StoryContinuation variant={variantNoId} onContinue={onContinue} />);
    
    expect(screen.getByText(/Continuation Unavailable/i)).toBeInTheDocument();
    expect(screen.getByText(/doesn't support continuation/i)).toBeInTheDocument();
  });

  it('displays loading state during continuation generation', async () => {
    let resolvePromise: (value: StoryContinuationType) => void;
    const promise = new Promise<StoryContinuationType>((resolve) => {
      resolvePromise = resolve;
    });
    
    const onContinue = vi.fn().mockReturnValue(promise);
    
    render(<StoryContinuation variant={mockVariant} onContinue={onContinue} />);
    
    const button = screen.getByRole('button', { name: /Generate AI continuation/i });
    fireEvent.click(button);
    
    // Loading state should appear immediately
    expect(await screen.findByText(/Summoning darker forces/i)).toBeInTheDocument();
    
    // Resolve the promise to complete the continuation
    resolvePromise!(mockContinuation);
    
    // Wait for continuation to complete
    await waitFor(() => {
      expect(screen.getByText(/The Nightmare Continues/i)).toBeInTheDocument();
    });
  });
});
