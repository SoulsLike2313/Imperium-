# ORGAN_PORT_CONTRACT_V1

## Why organ ports exist
Organ ports provide a stable, machine-readable way for each organ to report its own continuity state.
The immediate goal is to let continuity packaging evolve from a central scanner toward collector/orchestrator queries.

## Future continuity query flow
1. Continuity executor issues a query payload per organ.
2. Organ self-report port returns a contract-compliant response JSON.
3. Executor stores response + receipt and updates continuity indexes/metrics.
4. Missing ports remain non-fatal until implemented.

## Minimum valid self-report content
A valid self-report response must contain:
- organ identity
- explicit implementation status
- current state summary
- honest metrics availability
- known blockers
- next recommended actions
- evidence references
- receipt reference

## How an organ should inspect its own state
An organ must inspect only its own implemented scripts/data paths and must not claim data it cannot verify.
If no implementation exists, it must return NOT_IMPLEMENTED or NOT_YET_AVAILABLE with explicit blockers.

## Receipt requirements
Each self-report run must write a receipt containing:
- input query reference
- output response path
- status
- generation timestamp
- restriction flags (no VM2 contact, no fake metrics)

## Anti-fake rule
Fake implementation is forbidden.
No organ may emit PASS/active telemetry without real scripts and test evidence.
Contract-only ports must remain clearly marked as such.

## Ownership boundary
BUILD_CONTINUITY_PACK is expected to become Administratum-owned later, but Administratum is not implemented in 0016B.

## Audit boundary
Inquisition is expected to audit organ self-reports later, but Inquisition is not implemented in 0016B.

## Astronomicon boundary
Astronomicon remains a separate future organ role and is not equivalent to Administratum ownership.
