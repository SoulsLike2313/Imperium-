# GENERATED ARTIFACTS POLICY

Status: PASS_AS_SKELETON_CONTRACT

Rules:
- Generated Python cache files are excluded from clean source/control bundles.
- Excluded patterns: `__pycache__/`, `*.pyc`, `*.pyo`.
- Compile evidence must be represented by receipts/reports, not shipped cache files.
- Cache files are not source of truth and must not be registered as tools.
- Runtime implementation evidence belongs to later implementation tasks, not this cleanup pack.
