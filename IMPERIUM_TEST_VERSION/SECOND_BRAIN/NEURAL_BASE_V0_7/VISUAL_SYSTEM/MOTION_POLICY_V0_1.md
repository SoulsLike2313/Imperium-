# MOTION POLICY V0.1

## Allowed Motion
- Slow background drift.
- Slow brain pulse.
- Selected connector pulse (interaction-bound).
- Hover transform and opacity transitions.
- Receipt/task appear animation.

## Forbidden Motion
- Multiple independent infinite glows across many nodes.
- Animated blur/filter/box-shadow across many elements.
- Particle storms or burst-heavy effects.
- Motion implying backend progress without receipt.
- Any state that can be understood only through motion.

## Reduced Motion Requirement
- Reduced-motion mode must disable non-essential loops.
- Semantic state must remain readable with motion disabled.
- Brain/background fallback must remain visually coherent but static.
