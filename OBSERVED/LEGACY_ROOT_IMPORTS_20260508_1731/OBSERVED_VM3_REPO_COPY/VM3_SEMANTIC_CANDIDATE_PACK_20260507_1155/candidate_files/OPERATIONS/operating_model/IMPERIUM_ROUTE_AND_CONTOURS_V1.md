# IMPERIUM Route And Contours V1

Canonical route:

`Worker local implementation/proof -> full machine PASS + owner acceptance -> separate sync/admission on Throne -> post-admission fanout refresh -> Inquisition/Mechanicus closure chain -> owner decision`

## Phase Definitions

1. Worker local proof
- Purpose: heavy execution evidence generation on worker contour local work copy only.
- Inputs: task scope, constraints, tool outputs.
- Outputs: bounded proof package with hashes and logs.

2. PASS and owner acceptance gate
- Purpose: explicit machine PASS + owner acceptance before any Throne admission motion.
- Inputs: worker proof package and machine verdict surfaces.
- Outputs: accepted candidate marker for separate admission step.

3. Separate sync/admission on Throne
- Purpose: canonical intake/admission as a dedicated step, not worker execution.
- Inputs: accepted candidate manifest, hashes, policy checks.
- Outputs: admitted canonical head or explicit block.

4. Post-admission fanout refresh
- Purpose: distribute admitted canonical head to worker copies (VM1/PC refresh path).
- Inputs: admitted canonical head and fanout target map.
- Outputs: worker refresh evidence and deterministic fanout record.

5. PC proof buffer
- Purpose: owner-visible prep lane, candidate packaging, and handoff quality control.
- Inputs: VM proof packages and local operator checks.
- Outputs: bounded candidate package for Custodes intake.

6. Custodes review/admission
- Purpose: canonical gate review and bounded admission decision.
- Inputs: candidate manifest, hashes, policy checks.
- Outputs: PASS/WARN/FAIL chain and merge proposal/execute outputs.

7. Inquisition audit
- Purpose: policy/purity audit after technical verdict.
- Inputs: technical verdict + constitutional/policy evidence.
- Outputs: structured audit verdict artifact.

8. Adeptus Mechanicus verdict
- Purpose: technical integrity verdict over admitted candidate.
- Inputs: admitted diff set, build/lint/smoke evidence.
- Outputs: structured technical verdict artifact.

9. Owner decision
- Purpose: sovereign final authority for canon motion.
- Inputs: Custodes + Mechanicus + Inquisition artifacts.
- Outputs: accept/defer/reject decision artifact.

## Contour Roles

- Throne (Ubuntu): only canonical truth center.
- PC (Windows): support/audit/control/proof-buffer contour only.
- VM1, VM2, VM3: equal-class worker contours (numbers are communication labels, not ranks).
- Current session active worker for this operation: VM3.
- VM1: available as evidence/continuation worker by Owner switch.
- VM2: frozen/do-not-touch until Owner reactivation.
- Future PC Codex contour: deferred until maturity/limit recovery.

## Boundaries

- No second truth center.
- Worker contours must execute only in their own local work copies.
- Worker contours must not perform direct working edits on Throne.
- Sync/admission must be separate from worker implementation and must require full machine PASS + owner acceptance.
- No direct broad merge outside Custodes.
- No hidden merge logic in UI surfaces.
- PC is not a worker contour and is never a truth center.
- Active worker status is dynamic and task/session-bound.
