# FULL RUNTIME PERFORMANCE AUDIT RUNNER V0.1

## What It Does
- Runs a safe full-runtime audit for Second Brain V0.6 under the runtime safety contract.
- Uses an isolated runtime copy outside the git repo.
- Launches server on localhost, runs API checks, browser checks, required CSS/JS load checks, and FPS/load metrics when available.
- Writes compact receipts only:
  - `FULL_RUNTIME_PERFORMANCE_AUDIT_RECEIPT_V0_1.json/md`
  - `FULL_RUNTIME_SIDE_EFFECT_MANIFEST_V0_1.json/md`

## What It Does Not Do
- Does not edit source files (`app/server/css/js/html`).
- Does not optimize UI or runtime.
- Does not install dependencies or download browsers.
- Does not create or commit raw traces/HAR/screenshots/videos.

## Isolation Model
- Preferred isolation root: `E:/IMPERIUM_CONTEXT/LOCAL/RUNTIME_AUDITS/`.
- Fallback isolation root: OS temp directory outside repo.
- Copies required V0.6 + runtime data into isolated workspace.
- Runs server from isolated copy only.

## Run
```powershell
python IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/full_runtime_performance_audit_runner_v0_1.py
```

## Verdict Interpretation
- `PASS_FULL_RUNTIME_BASELINE`: runtime launch + API + required CSS/JS + FPS/load evidence + no repo pollution.
- `WARN_FULL_RUNTIME_BASELINE`: runtime evidence is usable but budget/perf warnings exist.
- `BLOCKED_*`: launch/isolation/API/assets/browser/FPS/shutdown/pollution blockers.

## Truth Rules
- Full runtime PASS is forbidden without required API checks and required CSS/JS load.
- FPS cannot be accepted when required assets or required API checks fail.
- Static-only frontend data is not full runtime truth.

## Output Budget & Raw Trace Policy
- Enforces GATE-U12 compact-report limits.
- Stores only compact counts/samples/top fields.
- Raw traces are disabled by default and must not be committed without explicit Owner gate.
