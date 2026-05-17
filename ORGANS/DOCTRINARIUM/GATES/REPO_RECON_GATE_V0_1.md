# REPO RECON GATE V0.1

## Gate Law
NO_REPO_RECON_NO_WORK.

## Purpose
Define mandatory reconnaissance checks that must run before non-trivial task execution in IMPERIUM.

## Mandatory Checks
1. Git truth check:
- repo root path
- branch
- `HEAD`
- `origin/master`
- short status summary

2. Main canon/lore scan:
- identify active meaning/lore areas in main tree
- list touched/not-touched canon zones

3. `IMPERIUM_TEST_VERSION` useful technology scan:
- identify reusable scripts/tools/components
- classify as candidate-only until gate-approved

4. Script/tool scan:
- enumerate script candidates (`.py`, `.ps1`, `.sh`, `.bat`)
- detect unregistered or orphan script candidates where possible

5. Runtime/artifact/cache candidate scan:
- identify generated-output zones, cache folders, and artifact-like paths
- mark as cleanup candidates only

6. Risk and forbidden path scan:
- confirm no forbidden path edits are planned
- list stop conditions tied to path or mutation risk

7. Guiding plan comparison:
- verify task intent aligns with current epoch doctrine and gatepack
- if mismatch detected -> stop and request clarification

8. Touched/not-touched declaration:
- explicit list of paths that will be touched
- explicit list of paths guaranteed untouched

## Stop Conditions
- HEAD mismatch against required task start hash
- scope cannot be maintained
- forbidden paths would be changed
- required receipts cannot be generated
- uncertainty about runtime/canon/test boundary

## Required Receipts
- Git truth snapshot (head/branch/status)
- Recon JSON report
- Recon Markdown report
- Gate acknowledgment block in task artifact
- Final touched/not-touched evidence
