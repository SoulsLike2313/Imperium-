# V1 Evidence and Receipt Contracts

## Canonical evidence model
- Canonical evidence is machine-readable JSON with deterministic fields.
- Optional markdown summaries are human support artifacts and cannot override JSON verdicts.
- Every PASS or PASS_WITH_WARNINGS must provide non-empty evidence_paths.

## Retention and archive policy
- Routine evidence should be moved to an indexed archive after 14 days when operationally safe.
- Canonical receipts and history are not casually deleted.
- Archive movement requires archive index updates and provenance retention.

## Verdict integrity
- PASS is allowed only when required evidence exists and schema checks pass.
- PASS_WITH_WARNINGS is allowed only with explicit non-empty warnings.
- FAIL or STOP must include blockers and remediation evidence expectations.

## Receipt ownership
- Stage completion receipts are owned by Administratum.
- Dashboard action receipts are owned by Administratum with Sanctum as renderer.
- Law and canon read/change receipts are owned by Doctrinarium.
- Role and mode read receipts are owned by Officio Agentis.

## Final bundle manifest
- Final bundle manifest is mandatory for closure and certification.
- Manifest must include artifact paths, hashes, git head, and creation UTC.
