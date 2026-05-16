# LANGUAGE POLICY

## Scope
This policy applies to all files in IMPERIUM_TEST_VERSION.

## Rules

### Internal/Canonical Artifacts (ENGLISH ONLY)
The following must be written in English:
- JSON schemas
- Thread indexes
- Agent state files
- Agent instructions
- Protocol definitions
- Machine-readable status values
- Configuration files
- Script comments (technical)

### Owner-Facing Artifacts (RUSSIAN ALLOWED)
The following may be written in Russian:
- README files with `_RU` suffix
- Owner reports with `_RU` suffix
- UI labels in HTML (Owner-facing sections only)
- Final verdict comments for Owner

### Agent Response Rule
All agents must:
- Respond to Owner in Russian unless Owner explicitly requests another language
- Write all canonical/internal artifacts in English
- Use English for machine status values even in Russian reports

### Status Values (ALWAYS ENGLISH)
These values must always be English regardless of document language:
- PASS, FAIL, PARTIAL, BLOCKED, UNKNOWN
- COMMIT_OK, REPAIR_REQUIRED, REJECT
- READY, DELIVERED, ACCEPTED, IN_PROGRESS, ANSWERED
- HIGH, MEDIUM, LOW

### File Naming
- Internal files: English names
- Owner reports: May include `_RU` suffix for Russian versions
- Schemas: English names with `.json` extension

## Enforcement
- Mojibake scanner checks for encoding issues
- Language policy violations are findings, not blockers
- Canonical files with Russian content are flagged for review
