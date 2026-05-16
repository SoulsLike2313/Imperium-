# No Fake Green Policy

## Core Rule

NEVER report PASS when checks have not actually passed.

## What counts as fake green

- Reporting PASS without running the checker
- Ignoring FAIL results and claiming success
- Hardcoding PASS in scripts (unconditional sys.exit(0))
- Pasting old terminal output as current evidence
- Claiming "all tests pass" without running tests
- Declaring production readiness from scaffold/prototype
- Hiding warnings or errors in reports

## Acceptable honest statuses

- PASS — checks ran and passed
- PASS_WITH_WARNINGS — checks passed but warnings exist
- FAIL — checks ran and failed
- SCAFFOLD — structure exists but not functional
- MOCK — sample data, not real
- NOT_CONFIGURED — zone exists but has no real configuration
- NOT_IMPLEMENTED — feature is planned but not built
- BLOCKED — cannot proceed due to dependency
- READY_FOR_OWNER_REVIEW — work done, needs Owner approval

## Consequence of violation

Any fake green finding is an automatic FAIL for the entire task.
Trust in the verification system is the highest priority.
