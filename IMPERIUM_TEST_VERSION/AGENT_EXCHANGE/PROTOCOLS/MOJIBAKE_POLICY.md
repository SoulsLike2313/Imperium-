# Mojibake Policy

## Purpose

This policy defines how IMPERIUM_TEST_VERSION detects broken text encoding in canonical/internal files.

## Rule

Canonical and internal files must not contain raw mojibake text.

Examples must not include literal mojibake characters directly. Use descriptive placeholders or Unicode/codepoint notation instead.

## Blocked raw patterns

Do not write raw broken Cyrillic examples directly in policy, schema, protocol, state, or source files.

Use safe descriptions instead:

| Unsafe category | Safe description |
|---|---|
| broken Cyrillic small letters | LATIN CAPITAL ETH + currency/sign-like continuation bytes |
| broken Cyrillic continuation | LATIN CAPITAL N WITH TILDE + continuation byte sequence |
| broken smart quotes | mojibake form of typographic quote / dash |
| Latin extended corruption | LATIN CAPITAL A WITH TILDE followed by symbol bytes |

## Safe examples

Allowed safe notation:

- `U+00D0 U+00B0` for a broken Cyrillic small-a byte sequence.
- `U+00D1 U+0082` for a broken Cyrillic continuation sequence.
- `U+00E2 U+0080 U+009D` for a broken typographic quote sequence.
- `LATIN CAPITAL A WITH TILDE + symbol byte` for broad Latin-extended corruption.

## Severity

- Raw mojibake in canonical/internal docs: BLOCKER.
- Raw mojibake in generated scan reports: INFO unless it contaminates canonical sources.
- Raw mojibake in scanner pattern definitions: WARNING unless it causes false blockers.
- Owner-facing Russian UTF-8 text is allowed when the file is explicitly Owner-facing.

## Owner-facing exception

Russian text is allowed in Owner-facing files only, such as:

- `*_RU.md`
- Owner manual verification checklists
- Owner final reports
- human-facing Russian summaries

Russian text is not the same as mojibake. Valid UTF-8 Russian is allowed only in explicitly Owner-facing files.

## PASS condition

The scan may pass only when:

1. no raw mojibake exists in canonical/internal files;
2. detected examples are represented safely;
3. generated reports do not promote historical examples to blockers;
4. scanner failures are not hidden or downgraded without evidence.
