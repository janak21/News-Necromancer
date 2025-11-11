import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import IntensitySlider from './IntensitySlider';

describe('IntensitySlider', () => {
  const mockOnChange = vi.fn();

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  describe('Rendering', () => {
    it('renders with default value', () => {
      render(<IntensitySlider value={3} onChange={mockOnChange} />);
      expect(screen.getByText('Horror Intensity')).toBeInTheDocument();
      expect(screen.getByText('Dark Shadows')).toBeInTheDocument();
    });

    it('displays correct level label for each intensity', () => {
      const levels = [
        { value: 1, label: 'Gentle Whisper' },
        { value: 2, label: 'Creeping Dread' },
        { value: 3, label: 'Dark Shadows' },
        { value: 4, label: 'Nightmare Fuel' },
        { value: 5, label: 'Absolute Terror' },
      ];

      levels.forEach(({ value, label }) => {
        const { rerender } = render(<IntensitySlider value={value} onChange={mockOnChange} />);
        expect(screen.getByText(label)).toBeInTheDocument();
        rerender(<IntensitySlider value={1} onChange={mockOnChange} />);
      });
    });

    it('displays correct description for each intensity', () => {
      const { rerender } = render(<IntensitySlider value={1} onChange={mockOnChange} />);
      expect(screen.getByText('Subtle hints and mild unease')).toBeInTheDocument();

      rerender(<IntensitySlider value={5} onChange={mockOnChange} />);
      expect(screen.getByText('Maximum horror intensity and existential dread')).toBeInTheDocument();
    });

    it('displays correct preview text for each intensity', () => {
      const previews = [
        { value: 1, text: 'A mysterious shadow flickered at the edge of your vision...' },
        { value: 2, text: 'The air grew cold as an unseen presence drew near, watching...' },
        { value: 3, text: 'Ghostly whispers echoed through the darkness, speaking your name...' },
        { value: 4, text: 'Terror gripped your soul as the nightmare manifested before you...' },
        { value: 5, text: 'Reality shattered as cosmic horrors beyond comprehension consumed all hope...' },
      ];

      previews.forEach(({ value, text }) => {
        const { rerender } = render(<IntensitySlider value={value} onChange={mockOnChange} />);
        expect(screen.getByText(text)).toBeInTheDocument();
        rerender(<IntensitySlider value={1} onChange={mockOnChange} />);
      });
    });

    it('renders all 5 intensity markers', () => {
      const { container } = render(<IntensitySlider value={3} onChange={mockOnChange} />);
      const markers = container.querySelectorAll('.intensity-marker');
      expect(markers).toHaveLength(5);
    });

    it('marks the current intensity level as active', () => {
      const { container } = render(<IntensitySlider value={3} onChange={mockOnChange} />);
      const activeMarkers = container.querySelectorAll('.intensity-marker.active');
      expect(activeMarkers).toHaveLength(1);
      expect(activeMarkers[0].textContent).toContain('3');
    });
  });

  describe('Slider Interaction', () => {
    it('calls onChange when slider is moved', () => {
      render(<IntensitySlider value={3} onChange={mockOnChange} />);
      const slider = screen.getByRole('slider', { name: 'Horror intensity level' });
      
      fireEvent.change(slider, { target: { value: '4' } });
      
      expect(mockOnChange).toHaveBeenCalledWith(4);
      expect(mockOnChange).toHaveBeenCalledTimes(1);
    });

    it('handles slider changes to minimum value', () => {
      render(<IntensitySlider value={3} onChange={mockOnChange} />);
      const slider = screen.getByRole('slider');
      
      fireEvent.change(slider, { target: { value: '1' } });
      
      expect(mockOnChange).toHaveBeenCalledWith(1);
    });

    it('handles slider changes to maximum value', () => {
      render(<IntensitySlider value={3} onChange={mockOnChange} />);
      const slider = screen.getByRole('slider');
      
      fireEvent.change(slider, { target: { value: '5' } });
      
      expect(mockOnChange).toHaveBeenCalledWith(5);
    });
  });

  describe('Marker Button Interaction', () => {
    it('calls onChange when marker button is clicked', () => {
      render(<IntensitySlider value={3} onChange={mockOnChange} />);
      const marker = screen.getByRole('button', { name: 'Set intensity to Nightmare Fuel' });
      
      fireEvent.click(marker);
      
      expect(mockOnChange).toHaveBeenCalledWith(4);
    });

    it('allows clicking on all marker buttons', () => {
      render(<IntensitySlider value={3} onChange={mockOnChange} />);
      
      const markers = [
        { name: 'Set intensity to Gentle Whisper', value: 1 },
        { name: 'Set intensity to Creeping Dread', value: 2 },
        { name: 'Set intensity to Dark Shadows', value: 3 },
        { name: 'Set intensity to Nightmare Fuel', value: 4 },
        { name: 'Set intensity to Absolute Terror', value: 5 },
      ];

      markers.forEach(({ name, value }) => {
        mockOnChange.mockClear();
        const marker = screen.getByRole('button', { name });
        fireEvent.click(marker);
        expect(mockOnChange).toHaveBeenCalledWith(value);
      });
    });
  });

  describe('Disabled State', () => {
    it('disables slider when disabled prop is true', () => {
      render(<IntensitySlider value={3} onChange={mockOnChange} disabled={true} />);
      const slider = screen.getByRole('slider');
      
      expect(slider).toBeDisabled();
    });

    it('disables marker buttons when disabled prop is true', () => {
      const { container } = render(<IntensitySlider value={3} onChange={mockOnChange} disabled={true} />);
      const markers = container.querySelectorAll('.intensity-marker');
      
      markers.forEach(marker => {
        expect(marker).toBeDisabled();
      });
    });

    it('slider is disabled and cannot be interacted with', () => {
      render(<IntensitySlider value={3} onChange={mockOnChange} disabled={true} />);
      const slider = screen.getByRole('slider');
      
      expect(slider).toBeDisabled();
      expect(slider).toHaveAttribute('disabled');
    });

    it('does not call onChange when disabled marker is clicked', () => {
      render(<IntensitySlider value={3} onChange={mockOnChange} disabled={true} />);
      const marker = screen.getByRole('button', { name: 'Set intensity to Absolute Terror' });
      
      fireEvent.click(marker);
      
      expect(mockOnChange).not.toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('has proper aria-label for slider', () => {
      render(<IntensitySlider value={3} onChange={mockOnChange} />);
      const slider = screen.getByRole('slider', { name: 'Horror intensity level' });
      
      expect(slider).toBeInTheDocument();
    });

    it('has proper aria-labels for marker buttons', () => {
      render(<IntensitySlider value={3} onChange={mockOnChange} />);
      
      expect(screen.getByRole('button', { name: 'Set intensity to Gentle Whisper' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Set intensity to Absolute Terror' })).toBeInTheDocument();
    });

    it('has proper title attributes for marker buttons', () => {
      render(<IntensitySlider value={3} onChange={mockOnChange} />);
      const marker = screen.getByRole('button', { name: 'Set intensity to Dark Shadows' });
      
      expect(marker).toHaveAttribute('title', 'Dark Shadows');
    });
  });
});
