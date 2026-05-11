# Core Orbit Optimization Report — Sanctum Qt v0.29

Patched at: 2026-05-11T20:02:37+03:00

## Problem

When the Transfer panel was closed, the central map became too wide and QPainter workload scaled up with the viewport. FPS dropped. The central body also still looked too abstract and the organ orbits needed clearer structure.

## Fix

- Bounded active map render zone to avoid unbounded paint cost.
- Added darker side margins when viewport is wider than the bounded scene.
- Rebuilt central planet with layered sphere, glow, equator, latitude/longitude arcs, and highlight.
- Rebuilt organ orbit layout with clearer lanes and labels.
- Reduced excessive particle count while keeping motion.
- Added precise timer and opaque/no-background paint flags.
- Improved orbital ring clarity and center composition.

## Expected result

- Closing Transfer panel should no longer heavily increase render cost.
- Planet should read as a real central command-world rather than just a dot.
- Organ orbits should be more understandable.
- FPS should be more stable.
