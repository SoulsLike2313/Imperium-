# VALIDATION Report

Compile:
- passed: True

JSON parse:
- verdict: PASS_JSON_PARSE
- parsed files: 35
- parse errors: 0

Scripts --help:
- failed count: 0

Launch card validation:
- verdict: PASS_VALIDATE_TASK_LAUNCH_CARD

Read-first receipt validation (sample):
- log: 05_VALIDATION/validate_read_first_receipt.log

Policy refs validation (example card):
- log: 05_VALIDATION/validate_policy_refs.log

Readonly safety scan (Explorer v1_0a):
- verdict: PASS_READONLY_SAFETY_SCAN

Explorer proof chain:
- static verdict: PASS_STATIC_READ_ONLY_SCAN
- truth verdict: PASS_TRUTH_SNAPSHOT_READY_FOR_SCREENSHOT_COMPARE
- autoscreenshot verdict: PASS_AUTOSCREENSHOT_TRUTH_COMPARE
- autoscreenshot checks_failed: 0
