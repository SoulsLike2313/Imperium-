# VISUAL GATES - CSS Examples

## HIGH/VISUAL-ON

All visual effects active:

```css
/* Star field - full density */
body::after {
  background-image: 22 radial-gradients;
  animation: star-drift 200s linear infinite;
}

/* Header scan line */
header::before {
  animation: header-scan 6s ease-in-out infinite;
}

/* Brand icon animation */
.brand-icon {
  animation: brand-pulse 4s ease-in-out infinite;
}

.brand-icon::after {
  animation: brand-ring-spin 8s linear infinite;
}
```

## MEDIUM/VISUAL-REDUCED

Reduced effects:

```css
/* Star field - half density */
body::after {
  background-image: 11 radial-gradients;
  animation: none;
}

/* Header static */
header::before {
  display: none;
}

/* Brand icon static */
.brand-icon {
  animation: none;
}
```

## LOW/VISUAL-MINIMAL

Minimal effects:

```css
/* Star field - minimal */
body::after {
  background-image: 6 radial-gradients;
  animation: none;
}

/* Background solid */
body::before {
  background: var(--bg);
}
```

## OFF/VISUAL-DISABLED

All animations disabled via media query:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
  
  body::after,
  .brand-icon,
  .brand-icon::after {
    animation: none;
  }
}
```