# DOCTRINARIUM DASHBOARD PATTERN REPORT

- Task: TASK-20260509-ADMINISTRATUM-ORGAN-DASHBOARD-AND-CONTINUITY-PACK-V0_1
- Run: RUN-20260509-223321-06ec59ea
- Source dashboard: DOCTRINARIUM_WEB_DASHBOARD_V0_8
- Source URL: http://127.0.0.1:8791

## What Makes v0.8 Work
- index.html
- style.css
- app.js
- dashboard_server.py
- DASHBOARD_STATUS.json or versioned status json
- dashboard launcher ps1
- DASHBOARD_REGISTRY.json
- ORGAN_UTILITY.json
- WORKBENCH_STATUS.json
- SCRIPT_BACKING_MAP.json
- technical registration receipt
- dashboard manifest and sha256 sums

## Server Pattern
- tech: Python ThreadingHTTPServer + SimpleHTTPRequestHandler
- binding: 127.0.0.1 fixed local port
- static_serving: serves dashboard root (index/css/js)
- api_style: JSON endpoints with explicit status codes and error payloads
- subprocess_pattern: calls PowerShell launcher/scripts for real backend actions
- security_notes: endpoint target whitelist for open-folder actions

## app.js Pattern
- data_source: /api/data polling/reload
- render_style: single-page sections with card/table rendering from JSON
- actions: buttons mapped to explicit backend endpoints; no fake local-only success
- state: client-side state object + renderAll pipeline
- error_signal: toast/error surface and reload after action

## CSS Pattern
- approach: tokenized color vars + dashboard panel system + responsive grid
- ui_type: organ diagnostics UI, not canonical source-of-truth
- note: visual style can differ; script-backing/evidence plumbing is the mandatory part

## API Endpoints Observed
- GET /api/data -> aggregate organ status/gaps/laws/paths
- POST /api/refresh -> run backend refresh script
- POST /api/open-organ -> open local organ folder (safe path)
- POST /api/open -> open whitelisted local folders

## Playwright Audit Pattern
- Verdict: PASS_PLAYWRIGHT_V0_8_VISUAL_FUNCTIONAL_AUDIT
- page loads
- metrics render
- navigation routes
- api response
- interaction smoke
- no console/page errors

## Registry/Status/Manifest/Receipt Pattern
- dashboard_registry: declares current dashboard id/version/url/launcher/manifest
- organ_utility: declares utility role, forbidden claims, limitations, visible outputs
- workbench_status: declares utility health/script-backed status/blockers
- script_backing_map: maps visible utility to concrete scripts
- manifest_hashes: dashboard-local file manifest and hashlist
- receipt: technical registration receipt references produced files and hashes

## Must Copy for Administratum
- script-backed endpoint for each active dashboard action
- explicit JSON API with failure propagation
- utility registry/status/backing files
- manifest+hashes+receipt evidence chain
- playwright or API smoke evidence report

## Must Not Copy Blindly
- Doctrinarium semantics (laws/doctrine metrics) as Administratum logic
- Doctrinarium refresh endpoint name/workflow
- Doctrinarium forbidden-claim text without Administratum-specific adaptation
- hardcoded paths to Doctrinarium reports as Admin source-of-truth

## Required Changes for Administratum
- domain model: memory/address/current_state/chronology/continuity pack
- single active action button: BUILD CONTINUITY PACK via POST /api/build-continuity-pack
- include latest continuity pack, comparison verdict, build receipt, and missing evidence surface
- port change to 8792 and separate launcher
- explicit limitation that continuity is not green/canon by default
