# Distributed Contours Capability

## Purpose
Define and verify safe PC-to-Ubuntu SSH capability before distributed execution is claimed.

## Current Status
Foundation only, manual confirmation required for real Ubuntu contour verification.

## What Works Now
- Profiles and schema exist.
- SSH capability checker supports dry-run and JSON receipt output.

## Foundation Only
- Real distributed task execution path is not implemented.

## Pass-Fail Logic
- `PASS` only after successful real SSH probe.
- `MANUAL_CONFIRMATION_REQUIRED` for dry-run or missing connection details.
- `BLOCKED` when required local tooling is absent.

## Manual Confirmation Required
- Owner-provided host/user/key and successful non-dry probe evidence.
