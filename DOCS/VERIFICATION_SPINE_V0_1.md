# VERIFICATION SPINE V0.1

Verification Spine v0.1 is the minimal product-grade backbone for repeatable repository verification.

## Components

- config: `src/imperium/config.py`
  - resolves root and runtime paths with ordered precedence.
  - supports `dev` and `operator` modes.
- path policy: `src/imperium/security/path_policy.py`
  - enforces root-constrained path access.
  - detects local absolute path tokens.
- command gateway: `src/imperium/security/command_gateway.py`
  - single raw subprocess boundary.
  - executes only allowlisted command IDs from `REGISTRY/COMMAND_ALLOWLIST.json`.
  - returns structured command receipts.
- receipt model/validator: `src/imperium/receipts/`
  - standardized verdict and receipt structures.
  - schema validation with explicit failure when `jsonschema` is unavailable.
- schemas: `schemas/*.json`
  - command receipt, warning receipt, verification report, and registry entries.
- gates: `scripts/*.py`
  - `no_pycache_tracked`
  - `no_raw_subprocess`
  - `public_private_boundary_scan`
  - `receipt_portability_check`
  - `verify_repo` aggregator

## Verdict Semantics

- `PASS`: no blockers and no warnings.
- `PASS_WITH_WARNINGS`: no blockers, but warnings or legacy debt findings exist.
- `FAIL`: blockers detected or gate execution failed.
- `BLOCKED`: policy prevented execution (for example disallowed command ID or mode).
