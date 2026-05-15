# SMOKE CHECKLIST

## Pre-Smoke

- [ ] Working directory clean (`git status --short` empty)
- [ ] Candidate in CANDIDATES/ folder
- [ ] Previous smoke results cleared

## Sanctum Smoke

- [ ] Run `powershell -File SANCTUM\RUN_SANCTUM_V0_29_QT.ps1`
- [ ] Window appears within 10 seconds
- [ ] No Python traceback in console
- [ ] Main window title correct
- [ ] All panels visible (or expected panels)
- [ ] Screenshot captured → SCREENSHOTS/

## Button Smoke (per button)

- [ ] Button visible
- [ ] Button clickable
- [ ] Button produces output (console or UI)
- [ ] No crash on click
- [ ] Receipt created (if applicable)

## Script Smoke

- [ ] Script exists at declared path
- [ ] `py -3 -m py_compile <script>` passes
- [ ] Script runs without immediate crash
- [ ] Script produces expected output type
- [ ] Exit code correct (0 = success, non-0 = failure)

## Post-Smoke

- [ ] Results saved to SMOKE_RESULTS/
- [ ] Screenshot saved to SCREENSHOTS/
- [ ] PASS/FAIL verdict recorded
- [ ] If FAIL: reason documented
