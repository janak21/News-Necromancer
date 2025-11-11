import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import SkeletonLoader, { SkeletonCard, SkeletonFeedList } from './SkeletonLoader';

describe('SkeletonLoader', () => {
  it('renders single skeleton element', () => {
    const { container } = render(<SkeletonLoader />);
    expect(container.querySelector('.skeleton-loader')).toBeInTheDocument();
  });

  it('renders multiple skeleton elements based on count', () => {
    const { container } = render(<SkeletonLoader count={3} />);
    const skeletons = container.querySelectorAll('.skeleton-loader');
    expect(skeletons).toHaveLength(3);
  });

  it('applies variant classes correctly', () => {
    const { container } = render(<SkeletonLoader variant="card" />);
    expect(container.querySelector('.skeleton-loader--card')).toBeInTheDocument();
  });

  it('applies custom width and height', () => {
    const { container } = render(<SkeletonLoader width="200px" height="50px" />);
    const skeleton = container.querySelector('.skeleton-loader') as HTMLElement;
    expect(skeleton.style.width).toBe('200px');
    expect(skeleton.style.height).toBe('50px');
  });

  it('handles numeric width and height', () => {
    const { container } = render(<SkeletonLoader width={100} height={50} />);
    const skeleton = container.querySelector('.skeleton-loader') as HTMLElement;
    expect(skeleton.style.width).toBe('100px');
    expect(skeleton.style.height).toBe('50px');
  });
});

describe('SkeletonCard', () => {
  it('renders skeleton card structure', () => {
    const { container } = render(<SkeletonCard />);
    expect(container.querySelector('.skeleton-card')).toBeInTheDocument();
    expect(container.querySelector('.skeleton-card__header')).toBeInTheDocument();
    expect(container.querySelector('.skeleton-card__body')).toBeInTheDocument();
    expect(container.querySelector('.skeleton-card__footer')).toBeInTheDocument();
  });
});

describe('SkeletonFeedList', () => {
  it('renders default number of skeleton cards', () => {
    const { container } = render(<SkeletonFeedList />);
    const cards = container.querySelectorAll('.skeleton-card');
    expect(cards).toHaveLength(3);
  });

  it('renders specified number of skeleton cards', () => {
    const { container } = render(<SkeletonFeedList count={5} />);
    const cards = container.querySelectorAll('.skeleton-card');
    expect(cards).toHaveLength(5);
  });
});
