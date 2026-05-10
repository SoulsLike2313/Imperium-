# VALIDATOR SMOKE TEST REPORT

- Verdict: PASS

## Cases
- CASE_01_MISSING_PASSPORT: pass_expected=True return_code=2 expected=missing Passport blocks
- CASE_02_MISSING_CODEX: pass_expected=True return_code=2 expected=missing Codex blocks
- CASE_03_FAKE_CANON_CLAIM: pass_expected=True return_code=2 expected=CANON_V0_1 claim without evidence blocks
- CASE_04_FOLDER_ONLY_ORGAN: pass_expected=True return_code=2 expected=folder-only organ fails standard
- CASE_05_LAW_MISSING_ENFORCEMENT: pass_expected=True return_code=2 expected=missing enforcement status reported
