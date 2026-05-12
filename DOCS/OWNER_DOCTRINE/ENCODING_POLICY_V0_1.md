# ENCODING_POLICY_V0_1

## Canonical Rule

- Canonical text encoding for IMPERIUM: `UTF-8 without BOM`.

## Implementation Rules

- Human-readable JSON files should be written with `ensure_ascii=False`.
- Python text I/O must use explicit `encoding="utf-8"`.
- HTML must include `<meta charset="utf-8">`.

## Legacy Source Rule

- `cp1251` is allowed only as a legacy source encoding for explicit conversion to UTF-8.
- `cp1251` is not an allowed target encoding for new or updated operational files.

## Scope Safety Rule

- Old artifacts/archives are not mass-normalized without explicit task scope and evidence.
