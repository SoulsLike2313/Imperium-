# Flicker Stabilization Report

Patched at: 2026-05-11T19:40:07+03:00

## Problem

Sanctum v0.28 inherited the v0.26 animated planet map loop. The map canvas was fully deleted and redrawn every 150 ms, which caused hard visible flicker.

## Fix

- Disabled continuous canvas redraw by default.
- Kept redraw on task selection / refresh / hover events.
- Removed forced canvas update during redraw.
- Kept animate() function as a future optional loop, but slowed and gated by animation_enabled = False.

## Expected result

Sanctum v0.28 should behave as a stable dashboard instead of a constantly repainting animation surface.

## Tradeoff

Planet pulse/rotation animation is disabled for now. This is acceptable for command dashboard stability.
