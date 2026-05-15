# Stage Decomposition Checklist

## Source Integrity
- [ ] Raw source files frozen and hashed.
- [ ] Manifest references real source paths.
- [ ] Source hash verification passes.

## Advisory/Canon Separation
- [ ] Advisory references marked non-canonical.
- [ ] No direct canon promotion without owner decision.
- [ ] Candidate items tagged with promotion status.

## Ownership Boundary
- [ ] Organ ownership responsibilities explicitly declared.
- [ ] No ownership theft across organs.
- [ ] External integration points documented as consumer-only where needed.

## Stage Dependency Order
- [ ] Dependency chain explicit.
- [ ] No circular dependencies.
- [ ] Irreversible actions gated behind prior PASS checks.

## PASS Criteria
- [ ] Each stage has measurable PASS criteria.
- [ ] PASS criteria include required evidence.
- [ ] PASS criteria include deterministic checker expectation.

## STOP Criteria
- [ ] Each stage has explicit STOP conditions.
- [ ] STOP includes failed checker and missing evidence.
- [ ] STOP includes ownership and scope violations.

## Evidence Paths
- [ ] Evidence paths declared per stage.
- [ ] Paths point to machine-readable artifacts.
- [ ] Evidence paths are verifiable in repository/runtime context.

## Script/Check Order
- [ ] Script creation order matches dependency order.
- [ ] Checker execution order documented.
- [ ] Aggregated check_all order documented.

## Schema Validation
- [ ] All JSON schemas parse.
- [ ] Required fields listed.
- [ ] Schema registry references are current.

## Fake Green Prevention
- [ ] No PASS without evidence.
- [ ] PASS_WITH_WARNINGS includes non-empty warnings.
- [ ] Disabled features are explicitly marked disabled.

## Registration Readiness
- [ ] Task manifest exists and parses.
- [ ] Stage map exists and parses.
- [ ] Source references and evidence requirements exist.

## Commit Readiness
- [ ] Diff limited to intended scope.
- [ ] Validation reports recorded.
- [ ] Git truth captured before and after.
