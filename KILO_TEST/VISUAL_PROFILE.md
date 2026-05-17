# VISUAL PROFILE - KILO_TEST

## Visual Quality Levels

This document defines the visual quality profiles for the Neural Map V0.6.

### HIGH (Default)
- All animations enabled
- Full star field with 22 stars
- Gradient backgrounds with nebula effects
- Header scan line animation
- Brand icon pulse animation
- All glow effects active

### MEDIUM
- Reduced star field (11 stars)
- Simplified gradients (2 layers)
- Header scan line disabled
- Brand icon static
- Basic glow effects only

### LOW
- Minimal star field (6 stars)
- Solid background color
- No animations
- Static UI elements
- No glow effects

### OFF
- Static background only
- No gradients
- No animations
- Minimal CSS effects
- Best performance mode

## Implementation

The visual level can be controlled via CSS classes or `prefers-reduced-motion` media query.

```css
/* Force LOW visual mode */
.visual-low { /* CSS rules */ }

/* Force OFF visual mode */
.visual-off { /* CSS rules */ }
```

## Performance Notes

- Original CSS: 1610 lines with ~20 keyframes and heavy gradients
- Optimized CSS: ~560 lines with reduced keyframes and simplified backgrounds
- Memory savings: ~65% reduction