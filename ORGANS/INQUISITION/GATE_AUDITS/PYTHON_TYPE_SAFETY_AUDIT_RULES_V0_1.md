# PYTHON TYPE SAFETY AUDIT RULES V0.1

## Attacks / Risks

### Attack: Script passes `py_compile` but returns wrong JSON shape
- Risk:
  - Syntax is valid while receipt contract is semantically broken.
- Block:
  - Require schema/field shape checks for promoted receipt/gate scripts.

### Attack: `Any` hides invalid receipt fields
- Risk:
  - Critical missing or wrong-typed fields pass silently.
- Block:
  - Require documented `Any` justification and narrowing before promotion.

### Attack: Optional `None` causes runtime report failure
- Risk:
  - Late failure or wrong fallback in report/gate output logic.
- Block:
  - Require explicit Optional handling in promoted scripts.

### Attack: Path/string confusion mutates wrong files
- Risk:
  - Wrong target writes or accidental pollution from unsafe path operations.
- Block:
  - Require typed path handling review for reusable/gate scripts.

### Attack: Untyped tool is copied into future agent factory
- Risk:
  - Type-chaos propagates into generated toolchains.
- Block:
  - Block agent-factory promotion without strict evidence.

### Attack: Type errors ignored because script once worked
- Risk:
  - One-time success is treated as reusable truth.
- Block:
  - Enforce maturity classification and promotion gates.

### Attack: Strict Pylance red zones ignored until too late
- Risk:
  - Contract drift reaches operational gates before detection.
- Block:
  - Treat strict red zones as pre-promotion blockers for required levels.

## Mandatory Blocks
- No promotion to reusable/gate/agent-factory tool without type-safety review evidence.
- No strict-clean claim without strict evidence artifact.
- No mass type refactor without dedicated gate scope and rollback path.

## Enforcement
- Unresolved risk above forces `FAIL` or `STOP` for promotion claims.
