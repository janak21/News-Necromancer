# Homepage Visual Polish - Design Tokens Reference

This document provides a reference for all CSS custom properties (design tokens) added for the Homepage Visual Polish feature.

## Typography Scale

### Hero Typography
- `--font-size-hero-title`: `clamp(2.5rem, 5vw + 1rem, 4.5rem)` - Fluid hero title size
- `--font-size-hero-subtitle`: `clamp(1.125rem, 2vw + 0.5rem, 1.5rem)` - Fluid subtitle size
- `--font-size-card-title`: `1.25rem` - Feature card title size
- `--font-weight-hero`: `700` - Bold weight for hero text
- `--line-height-hero`: `1.1` - Tight line height for hero
- `--line-height-body`: `1.6` - Comfortable body text line height

### Modular Typography Scale (1.25 ratio - Major Third)
- `--type-scale-1`: `1rem` (16px) - Base
- `--type-scale-2`: `1.25rem` (20px)
- `--type-scale-3`: `1.563rem` (25px)
- `--type-scale-4`: `1.953rem` (31px)
- `--type-scale-5`: `2.441rem` (39px)
- `--type-scale-6`: `3.052rem` (49px)
- `--type-scale-7`: `3.815rem` (61px)
- `--type-scale-8`: `4.768rem` (76px)

## Spacing Scale

### Homepage-Specific Spacing
- `--spacing-hero-top`: `4rem` - Top padding for hero section
- `--spacing-hero-bottom`: `3rem` - Bottom padding for hero section
- `--spacing-section-gap`: `4rem` - Gap between major sections
- `--spacing-cta-gap`: `2rem` - Gap between CTA buttons
- `--spacing-card-padding`: `2rem` - Internal padding for feature cards
- `--spacing-card-gap`: `1.5rem` - Gap between feature cards
- `--spacing-logo-padding`: `1.5rem` - Padding around logo

## Responsive Breakpoints

- `--breakpoint-mobile`: `640px`
- `--breakpoint-tablet`: `768px`
- `--breakpoint-desktop`: `1024px`
- `--breakpoint-wide`: `1280px`

### Mobile Adjustments (< 640px)
- `--spacing-hero-top`: `2.5rem`
- `--spacing-hero-bottom`: `2rem`
- `--spacing-section-gap`: `2.5rem`
- `--spacing-cta-gap`: `1.5rem`
- `--spacing-card-padding`: `1.5rem`
- `--spacing-card-gap`: `1rem`
- `--card-emoji-size`: `1.75rem`

### Extra Small Mobile (< 480px)
- `--spacing-hero-top`: `2rem`
- `--spacing-card-padding`: `1.25rem`

## Visual Effects

### Gradients
- `--gradient-hero-bg`: Radial gradient for hero background
- `--gradient-text-primary`: Linear gradient for text effects
- `--gradient-button-primary`: Subtle gradient for primary buttons
- `--gradient-card-hover`: Shimmer effect for card hover

### Glows
- `--glow-primary`: `0 0 20px rgba(138, 43, 226, 0.6)` - Base glow
- `--glow-primary-intense`: `0 0 30px rgba(138, 43, 226, 0.8)` - Intense glow
- `--glow-hover`: Multi-layer glow for hover states
- `--glow-button`: `0 0 16px rgba(167, 139, 250, 0.5)` - Button glow
- `--glow-card`: `0 0 24px rgba(167, 139, 250, 0.3)` - Card glow
- `--glow-text`: `0 2px 8px rgba(138, 43, 226, 0.4)` - Text shadow glow

### Shadows
- `--shadow-lift`: Elevated shadow for cards
- `--shadow-lift-hover`: Enhanced shadow for hover state

## Animation & Transitions

### Timing Functions
- `--transition-smooth`: `all 300ms cubic-bezier(0.4, 0, 0.2, 1)` - General smooth transition
- `--transition-lift`: Combined transform and shadow transition
- `--transition-glow`: Combined glow and border transition

## Button Hierarchy

### Button Sizes
- `--button-size-sm`: `2.5rem`
- `--button-size-md`: `3rem`
- `--button-size-lg`: `3.5rem`
- `--button-size-xl`: `4rem`

## Feature Cards

### Card Properties
- `--card-emoji-size`: `2rem` - Size of emoji icons
- `--card-hover-lift`: `-8px` - Vertical lift on hover
- `--card-border-default`: `1px solid rgba(167, 139, 250, 0.15)` - Default border
- `--card-border-hover`: `1px solid rgba(167, 139, 250, 0.4)` - Hover border

## Background Effects

- `--bg-noise-opacity`: `0.02` - Subtle texture opacity
- `--bg-gradient-overlay`: Dual radial gradient overlay

## Accessibility

### Reduced Motion
When `prefers-reduced-motion: reduce` is active:
- All glow effects are reduced to minimal values
- Transitions are disabled
- Animations are removed

### High Contrast Mode
Automatically adjusts colors for better visibility when `prefers-contrast: high` is active.

## Usage Examples

```css
/* Hero title with fluid typography */
.hero-title {
  font-size: var(--font-size-hero-title);
  font-weight: var(--font-weight-hero);
  line-height: var(--line-height-hero);
}

/* Primary button with glow */
.button-primary {
  height: var(--button-size-xl);
  box-shadow: var(--glow-button);
  transition: var(--transition-smooth);
}

.button-primary:hover {
  box-shadow: var(--glow-hover);
}

/* Feature card with lift effect */
.feature-card {
  padding: var(--spacing-card-padding);
  border: var(--card-border-default);
  transition: var(--transition-lift);
}

.feature-card:hover {
  transform: translateY(var(--card-hover-lift));
  border: var(--card-border-hover);
  box-shadow: var(--shadow-lift-hover);
}
```

## Notes

- All spacing values follow an 8pt grid system for consistency
- Typography scale uses a 1.25 (Major Third) ratio for harmonious sizing
- Fluid typography uses `clamp()` for responsive scaling without media queries
- All animations respect user motion preferences
- Color values maintain WCAG AA contrast ratios
