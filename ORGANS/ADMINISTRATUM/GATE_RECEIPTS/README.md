# GATE RECEIPTS LEDGER

A gate receipt is a machine-auditable record proving a gate check was executed and what verdict it produced.

## Location
Gate receipts live in:
- `ORGANS/ADMINISTRATUM/GATE_RECEIPTS/`

Index file:
- `ORGANS/ADMINISTRATUM/GATE_RECEIPTS/gate_receipt_index_v0_1.jsonl`

## Minimum Receipt Fields
- `task_id`
- `gate_or_check_id`
- `timestamp_utc`
- `current_head`
- `verdict`
- `evidence_paths`
- `notes`

## No Fake Green Rule
Never mark receipt verdict `PASS` without concrete evidence paths that can be opened and verified.

## Append Rule For Future Servitors
- Append one JSON object per line to the JSONL index.
- Do not rewrite historical lines.
- Keep each line valid JSON.
- Include absolute or repo-relative evidence paths.
