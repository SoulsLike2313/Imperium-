from pathlib import Path

p = Path("RUN_ALL.ps1")
s = p.read_text(encoding="utf-8-sig")

old = """param(
    [switch]$SkipNewComponents,
    [switch]$OnlyCore,
    [switch]$Verbose
)"""

new = """param(
    [switch]$SkipNewComponents,
    [switch]$OnlyCore,
    [switch]$Verbose,
    [switch]$CandidateMode
)"""

if "[switch]$CandidateMode" not in s:
    if old not in s:
        raise SystemExit("RUN_ALL param block not found")
    s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8")
    print("PATCHED_RUN_ALL_PARAM")
else:
    print("CandidateMode already present")
