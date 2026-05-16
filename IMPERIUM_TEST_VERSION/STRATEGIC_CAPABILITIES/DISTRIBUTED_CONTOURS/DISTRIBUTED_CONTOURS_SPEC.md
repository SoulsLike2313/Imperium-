# DISTRIBUTED CONTOURS SPECIFICATION

**Version:** 1.1.0  
**Status:** FOUNDATION  
**Created:** 2026-05-16

## Purpose
Define the safe capability foundation for distributing work between PC contour and Ubuntu laptop contour.

## Current Status
- Schema/templates exist.
- SSH capability checker exists.
- Ubuntu contour verification is not proven yet.

## What Works Now
- Contour profile schema and templates are available.
- `ssh_capability_check.ps1` supports dry-run and explicit manual confirmation signaling.

## Foundation Only
- No proven automated task routing.
- No verified remote receipt transfer workflow.

## Pass-Fail Logic
- `PASS`: SSH check succeeds against real host with valid credentials.
- `MANUAL_CONFIRMATION_REQUIRED`: credentials/profile absent or dry-run only.
- `BLOCKED`: required tooling missing (e.g. ssh client unavailable).
- `FAIL`: actual SSH probe fails with provided credentials.

## Manual Confirmation Required
- Owner confirms correct Ubuntu host, key path, and account.
- Owner confirms remote environment readiness.

## Next Steps
1. Run real SSH check from PC contour.
2. Capture JSON receipt for laptop contour verification.
3. Implement task routing policy execution with audit trail.
