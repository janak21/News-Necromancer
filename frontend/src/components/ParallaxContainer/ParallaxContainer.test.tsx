import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import ParallaxContainer from './ParallaxContainer';

describe('ParallaxContainer', () => {
  let mockContext: CanvasRenderingContext2D;

  beforeEach(() => {
    mockContext = {
      clearRect: vi.fn(),
      fillRect: vi.fn(),
      beginPath: vi.fn(),
      closePath: vi.fn(),
      fill: vi.fn(),
      stroke: vi.fn(),
      arc: vi.fn(),
      moveTo: vi.fn(),
      lineTo: vi.fn(),
      quadraticCurveTo: vi.fn(),
      ellipse: vi.fn(),
      save: vi.fn(),
      restore: vi.fn(),
      translate: vi.fn(),
      rotate: vi.fn(),
      createRadialGradient: vi.fn(() => ({
        addColorStop: vi.fn(),
      })),
      createLinearGradient: vi.fn(() => ({
        addColorStop: vi.fn(),
      })),
    } as unknown as CanvasRenderingContext2D;

    HTMLCanvasElement.prototype.getContext = vi.fn(() => mockContext) as any;
    let rafId = 0;
    window.requestAnimationFrame = vi.fn(() => {
      return ++rafId;
    });
    window.cancelAnimationFrame = vi.fn();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders children content', () => {
    render(
      <ParallaxContainer>
        <div>Test Content</div>
      </ParallaxContainer>
    );
    
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('initializes canvas with correct context', () => {
    render(<ParallaxContainer><div>Content</div></ParallaxContainer>);
    
    expect(HTMLCanvasElement.prototype.getContext).toHaveBeenCalledWith('2d');
  });

  it('renders particles based on density', () => {
    render(
      <ParallaxContainer particleDensity="high">
        <div>Content</div>
      </ParallaxContainer>
    );
    
    expect(mockContext.clearRect).toHaveBeenCalled();
  });

  it('applies parallax effect when enabled', () => {
    render(
      <ParallaxContainer enableParallax={true}>
        <div>Content</div>
      </ParallaxContainer>
    );
    
    expect(window.requestAnimationFrame).toHaveBeenCalled();
  });

  it('renders specified particle types', () => {
    render(
      <ParallaxContainer particleTypes={['bats', 'fog']}>
        <div>Content</div>
      </ParallaxContainer>
    );
    
    expect(mockContext.save).toHaveBeenCalled();
    expect(mockContext.restore).toHaveBeenCalled();
  });
});
