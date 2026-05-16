# Readability Fix — Applied after Owner rejection of AAA Pass V0.1

## Problem identified by Owner
- Interface too dark
- Core zones not visible enough
- Canvas over-darkened by vignette
- Zones hidden behind subtle atmosphere

## Fixes Applied

### CSS changes
- `--bg-deep`: #010306 → #030609 (lighter base)
- `--bg`: #020509 → #04080f
- `--border-*`: all raised by ~30% brightness
- `--text-*`: all raised for better readability
- Canvas vignette: reduced from 0.8 to 0.5 max opacity, starts at 60% not 50%
- Canvas grid: opacity 0.018 → 0.012, size 60px → 80px (less intrusive)
- Nebula background: opacity raised 0.07→0.10, 0.06→0.09, 0.025→0.04
- `core-halo-breathe`: 0.12/0.32 → 0.25/0.55 (much more visible)
- `core-breathe`: 0.45/0.85 → 0.65/1.0
- Pulse animations: all raised ~25% opacity
- Zone label: added `paint-order: stroke fill` + dark stroke for readability on any background
- Zone hover: brightness 1.6 → 1.7, drop-shadow stronger

### JS changes
- Zone gradient fill opacity: 0.42 → 0.65 (key fix — zones now clearly visible)
- Zone border stroke-width: 2 → 2.5 for WORKING zones
- Zone border fill: 0.06 → 0.10
- Strand primary opacity: 0.14 → 0.22
- Strand data opacity: 0.12 → 0.18
- Strand secondary opacity: 0.09 → 0.14
- Strand stroke-width: 1.8 → 2.0 primary, 1.2 → 1.5 data
- Strand shadow: 0.04 → 0.06
- Core border: 0.65 → 0.85 opacity, 2 → 2.5 stroke-width
- Core CW ring: 0.38 → 0.60 opacity, 1.5 → 2.0 stroke-width
- Core CCW ring: 0.22 → 0.38 opacity
- Core halo opacity: 0.5/0.7 → 0.8/1.0
- Health dots: #40d888 → #50e890, r=4 → r=4.5 for working dots
- MISSING color: #2e4a68 → #3d5a78 (slightly more visible)

### HTML SVG changes
- All zone gradients: stop-opacity raised from 0.75 to 0.9 at center
- All zone gradients: mid-stop raised from 0.35 to 0.55
- Core gradient: center 0.55 → 0.75, mid 0.35 → 0.55
- Core halo: 0.18 → 0.22

## Verification
- Server: PASS (port 8767)
- Health: 9/12 WORKING, 3/12 PARTIAL (honest)
- no_agent_api: true
- no_local_llm: true
- Register task: PASS (201)
- Launch task: PASS (200)
- Handoff block: generated
- Truth: preserved

## No Commit Performed
