# SANCTUM EXPERIMENTAL STATUS

- status: SUPER_EXPERIMENTAL_TRANSITIONAL_OPERATOR_DASHBOARD
- date: 2026-05-13
- owner_verdict: WORKING_BASELINE_ACCEPTED_AS_TEMPORARY_RUNTIME_NOT_FINAL_UI
- working_baseline: SANCTUM/sanctum_v0_29_qt.py
- rejected_line:
  - Sanctum EE
  - v0.30EE
  - R1
  - R2
- visual_dashboard_preview_status:
  - TASK-20260513-SANCTUM-DASHBOARD-SHELL-AND-REGISTRATION-CORRIDOR-V0_1_VM2_HANDOFF
  - technical prototype only
  - visual status rejected
  - not accepted as Sanctum UI
  - not to be treated as final dashboard direction

## Meaning

Sanctum is currently a working but experimental operator shell.

The accepted practical baseline is `SANCTUM/sanctum_v0_29_qt.py`.
It has useful operator functions, transfer controls, bundle listing, task visibility, and adaptive state panels.

However, Sanctum is not yet a finished application or stable design system.
It must be treated as an experimental transition layer until the dashboard architecture, UI factory, action registry, tests, and organ modules are properly formalized.

## Hard rules

1. Do not revive EE/R1/R2 unless Owner explicitly requests it.
2. Do not replace working operator behavior with a visual rewrite.
3. Do not call a generic empty HTML page "Sanctum Dashboard".
4. Dashboard work must preserve controllability, gates, receipts, paths, and no-fake-green rules.
5. Visual changes must be developed through ASSETS / DESIGN_SYSTEM / UI_LAB before integration.
6. Runtime logic and UI beauty must be separated.

## Intended direction

Sanctum should evolve into:

- beautiful operator dashboard shell;
- Python runtime/control core under the hood;
- organ dashboards embedded as modules/panels;
- actions routed through registry/gates/scripts/receipts;
- Playwright-testable UI where every button can be trusted;
- visual language based on accepted Sanctum screenshots and Owner-approved design references.

## Current decision

The VM2 standalone Registration Corridor Dashboard preview is not accepted as final UI.

Usable ideas from it may be salvaged later:
- state builder concept;
- dashboard state JSON;
- checker concept;
- registration corridor panel concept.

Rejected parts:
- generic visual style;
- empty cards;
- UNKNOWN state on open;
- file:// JSON autoload failure;
- lack of Sanctum visual identity.
