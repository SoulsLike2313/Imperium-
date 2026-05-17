# VISUAL LAYER CONTRACT V0.1

Hard rule: decorative layers must never encode live truth, health, readiness, task status, or PASS/FAIL.

## L0 Background Plate
- Purpose: atmospheric backdrop and depth.
- Allowed technology: static image, gradient mesh, low-cost canvas drift.
- Semantic data allowed: no.
- Performance budget notes: must stay below background-only render budget; no expensive full-screen filters.
- Allowed animations: very slow drift/parallax.
- Forbidden behaviors: status colors, counters, readiness words, flashing warnings.
- Required evidence: layer classification receipt + performance sample.

## L1 Core Brain Art Plate
- Purpose: central visual anchor object.
- Allowed technology: SVG/Canvas/model sprite, pre-baked texture sequence.
- Semantic data allowed: no.
- Performance budget notes: central object cost must not consume majority of frame budget.
- Allowed animations: slow pulse, subtle rotation, low-frequency luminance shift.
- Forbidden behaviors: PASS/FAIL rings, live health encoding, task progression implied by animation.
- Required evidence: animation policy check + performance receipt.

## L2 Semantic Topology
- Purpose: non-live structure map (zones, relations, naming).
- Allowed technology: SVG graph, DOM topology map, canvas connectors.
- Semantic data allowed: yes, static or receipt-bound semantic labels only.
- Performance budget notes: connector/node count must fit declared DOM/SVG budgets.
- Allowed animations: selected connector pulse on interaction only.
- Forbidden behaviors: autonomous status state changes without backend binding.
- Required evidence: truth-binding manifest link for every visible semantic label.

## L3 Ambient Particles
- Purpose: ambient motion and depth accent.
- Allowed technology: lightweight canvas particles with strict caps.
- Semantic data allowed: no.
- Performance budget notes: particle counts must stay under particle budget caps.
- Allowed animations: slow ambient drift.
- Forbidden behaviors: particle storms, burst spam, status color signaling.
- Required evidence: particle count receipt + reduced-motion compliance note.

## L4 Operator Surface
- Purpose: operator-facing panel, controls, and readable cards.
- Allowed technology: semantic HTML/DOM components, optional SVG icons.
- Semantic data allowed: yes, only with required backend source defined in truth-binding manifest.
- Performance budget notes: panel updates must avoid layout thrash and heavy paints.
- Allowed animations: hover transform/opacity, panel reveal.
- Forbidden behaviors: synthetic counters, fake-ready wording, green defaults without receipt.
- Required evidence: claim-to-source mapping, stale-state policy evidence.

## L5 Gate/Receipt Overlays
- Purpose: explicit gate state, receipt identity, stale/fresh indicators.
- Allowed technology: DOM overlay badges and receipt-linked labels.
- Semantic data allowed: yes, mandatory.
- Performance budget notes: overlays must be text-first and lightweight.
- Allowed animations: appear/disappear transitions for new receipts/tasks.
- Forbidden behaviors: hidden errors, silent pass labels, auto-green without evidence.
- Required evidence: receipt IDs, timestamp, source binding, fake-green audit checks.
