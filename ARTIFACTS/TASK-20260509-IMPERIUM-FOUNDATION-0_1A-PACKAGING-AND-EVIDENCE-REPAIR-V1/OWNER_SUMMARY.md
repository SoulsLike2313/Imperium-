# IMPERIUM Foundation 0.1A Packaging and Evidence Repair

TASK_ID: TASK-20260509-IMPERIUM-FOUNDATION-0_1A-PACKAGING-AND-EVIDENCE-REPAIR-V1

STATUS:
PASS_FOUNDATION_0_1A_CONTENT_PACKAGE_READY_FOR_SPECULUM_REVIEW

## Purpose

This repair package responds to Speculum review of Foundation 0.1.

It fixes the main evidence problem by creating a CONTENT PACKAGE:
- actual ORGANS snapshot;
- actual EXPLORER v1_0A source/proof tools if present;
- actual policy/schema/script files if present in ORGANS;
- actual validation reports;
- clean packaging finalization model.

## Packaging model

CONTENT_MANIFEST.json excludes:
- itself;
- SHA256SUMS.txt;
- 07_BUNDLE;
- final ZIP;
- final ZIP sidecar.

SHA256SUMS.txt includes:
- payload files;
- CONTENT_MANIFEST.json;
- not itself.

FINALIZATION_RECEIPT.json is external to zipped payload in 07_BUNDLE.

## Still not claimed

- No CONTINUITY_GREEN.
- No organs implemented.
- No Sanctum ready.
- No Aquarium ready.
- No E2E ready.
- No THRONE connected.
- No production automation ready.

## Missing inputs found by builder

[]
