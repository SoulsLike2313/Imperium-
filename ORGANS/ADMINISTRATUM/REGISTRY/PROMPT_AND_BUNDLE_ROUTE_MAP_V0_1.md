# Prompt and Bundle Route Map v0.1

## Route A: PC -> VM2 (Prompt Dispatch / Bundle Pull)
- SSH user/host: `vboxuser2@127.0.0.1`
- SSH port: `2223`
- SSH key (PC PowerShell): `$env:USERPROFILE\.ssh\imperium_pc_to_vm2_ed25519_20260418`
- VM2 prompt path: `/home/vboxuser2/IMPERIUM_WORK/VM2_PROMPTS`
- VM2 bundle outbox path: `/home/vboxuser2/IMPERIUM_WORK/VM2_BUNDLES`

## Route B: VM2 -> PC (External Context Maintenance)
- SSH user/host: `pc@10.0.2.2`
- SSH key (VM2): `/home/vboxuser2/.ssh/imperium_vm2_to_pc_ed25519_20260418`

## Canonical Bundle Intake/Review on PC
- Bundle inbox root: `E:\IMPERIUM_CONTEXT\LOCAL\VM2_BUNDLES`
- Bundle review root: `E:\IMPERIUM_CONTEXT\LOCAL\BUNDLE_REVIEWS`

## Canonical Bundle Outbox on VM2
- `/home/vboxuser2/IMPERIUM_WORK/VM2_BUNDLES/`

## Integrity and Truth Rules
- SHA256 file must be produced for each bundle.
- No-floating-master rule: do not claim completion on a moving branch reference.
- Exact HEAD rule: verify and record exact commit hash for task start and verification.

## Route Status (2026-05-14)
- PC -> VM2 route: confirmed.
- VM2 -> PC route: confirmed.
