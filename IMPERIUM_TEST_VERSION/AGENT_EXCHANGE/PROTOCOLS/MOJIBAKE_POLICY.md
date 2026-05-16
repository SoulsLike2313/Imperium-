# MOJIBAKE POLICY

## Definition
Mojibake is garbled text resulting from encoding/decoding errors, typically when UTF-8 text is misinterpreted as another encoding.

## Common Mojibake Patterns
The following patterns indicate mojibake and must be flagged:

### Cyrillic Mojibake (UTF-8 as Windows-1251/CP1252)
- `Ð` followed by Cyrillic-like characters
- `Ñ` followed by symbols
- `Ð°`, `Ð±`, `Ð²` etc.
- `Ñ‚`, `Ñ€`, `Ñ‹` etc.

### Latin Extended Mojibake
- `Â` before punctuation or spaces
- `Ã` followed by symbols
- `â€"`, `â€™`, `â€œ`

### Detection Regex Patterns
```
Ð[А-яЁё]
Ñ[‚€™œ]
Â[^\w]
Ã[^\w]
â€[""''—–]
```

## Severity Levels

### BLOCKER
- Mojibake in JSON schema files
- Mojibake in protocol definitions
- Mojibake in agent state files
- Mojibake in thread indexes

### WARNING
- Mojibake in markdown documentation
- Mojibake in HTML templates
- Mojibake in comments

### INFO
- Mojibake in generated reports (may be regenerated)
- Mojibake in log files

## Resolution
1. Identify source file encoding
2. Re-save with UTF-8 encoding (with BOM if needed for Windows)
3. Verify content is readable
4. Re-run mojibake scanner

## Scanner Usage
```powershell
py -3 AGENT_EXCHANGE/TOOLS/mojibake_scan.py --scope IMPERIUM_TEST_VERSION
```

## Policy Enforcement
- All new canonical files must pass mojibake scan
- Existing mojibake is tracked as technical debt
- Main canon mojibake is recorded but not fixed (read-only)
