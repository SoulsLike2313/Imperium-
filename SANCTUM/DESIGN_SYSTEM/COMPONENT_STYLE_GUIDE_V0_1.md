# COMPONENT_STYLE_GUIDE_V0_1

## Confirmed Baseline Guidance
- Keep operator readability above decorative effects.
- Keep actionable controls explicit and keyboard-friendly where possible.
- Preserve runtime safety: visual layer must not silently alter command behavior.

## Proposed Component Direction (Step 7.2, Pending Owner Confirmation)

### Core / Orbit Panel
- Central core node with restrained glow halo.
- Orbit nodes represent organs/actions as labeled points.
- Network links should remain thin and non-flickering.

### Evidence / Truth Strip
- Dedicated high-contrast strip for Git truth, route truth, and checker verdicts.
- Use status chips: `PASS`, `WARN`, `BLOCKED` with clear color roles.

### Bundle Panel
- Show canonical route first and explicitly label legacy fallback sources.
- Show source directory, mtime, and dedupe result for each bundle.

### Cards and Metrics
- Use layered dark cards with consistent spacing/radius scales.
- Avoid over-saturated gradients behind dense text.

### Motion
- Keep animation restrained and state-driven.
- Forbid heavy background animation in dense operator views.

Raw screenshot is evidence, not canon.
Servitor interpretation is proposal, not canon.
Owner confirmation turns interpretation into accepted visual rule.
