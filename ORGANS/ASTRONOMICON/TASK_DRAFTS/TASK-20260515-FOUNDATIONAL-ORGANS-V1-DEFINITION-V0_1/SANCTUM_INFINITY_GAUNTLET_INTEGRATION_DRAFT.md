# Sanctum Infinity Gauntlet Integration Draft

Status: draft derived from Owner answers.

## Core metaphor

Sanctum is the Infinity Gauntlet of IMPERIUM.

It gathers the powers of all organs and displays their truth in one central command bridge, while preserving each organ's unique visual spirit.

Sanctum does not replace organ backends.
Sanctum does not repaint all organs into one flat style.
Sanctum aggregates, connects, and commands.

## Integration model

Each organ must expose:

- dashboard_state.json;
- dashboard_metrics.json;
- dashboard_actions.json;
- dashboard_panels.json;
- dashboard_i18n/en.json;
- dashboard_i18n/ru.json;
- dashboard_style.json.

Sanctum reads these organ dashboard contracts and renders a unified cockpit.

## Sanctum shell structure

Proposed command bridge:

- top truth bar;
- global task corridor;
- organ orbit or organ grid;
- selected organ workspace;
- global warnings and blockers;
- command/action drawer;
- evidence/report viewer;
- continuity/handoff panel.

## Organ style preservation

Each organ contributes a visual note:

- Astronomicon: cosmic navigation, stage routes, stellar maps.
- Administratum: imperial archive, black-box ledger, bureaucratic truth.
- Officio Agentis: agent command hall, role matrix, contract seals.
- Doctrinarium: law chamber, canon tablets, gate verdicts, strict compliance.

Sanctum unifies these notes through shared layout, shared motion discipline, shared typography rules, shared evidence language, and shared status vocabulary.

## Data density rule

Sanctum must support many organs and metrics without chaos by using layered depth:

- Level 0: organ status;
- Level 1: key metrics;
- Level 2: panels/actions/reports;
- Level 3: raw evidence and JSON.

## Action safety

Sanctum actions must route through organ-defined action contracts.

No direct hidden execution.
No fake green.
No silent success.
Every meaningful action produces a report or receipt.
