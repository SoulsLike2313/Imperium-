# VM2 STAGE BUNDLE POLICY

A VM2 stage bundle must include:
- stage output
- STAGE_RECEIPT.md
- OUTPUT_MANIFEST.csv
- SHA256SUMS.txt
- optional BLOCKERS.md
- optional NOTES.md

Naming convention:
TASK-<id>__STAGE-<id>__CONTOUR-VM2__RUN-<id>__STAGE_BUNDLE.zip

Do not use latest bundle logic.
Use TASK_ID/STAGE_ID/CONTOUR_ID/RUN_ID.
