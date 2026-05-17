# REPORT OUTPUT BUDGET V0.1

## Principle
- Reports are evidence, not data dumps.
- NO_REPORT_AVALANCHE: generated evidence must stay compact, actionable, and reviewable.

## Why Report Avalanche Is Dangerous
- Oversized reports hide critical findings in noise.
- Commit size explodes and slows future Servitor operations.
- Gate review quality drops because signal is drowned by raw trace bulk.
- Recursive scanner/report behavior can create uncontrolled output growth.

## Default Report Budget
- max_report_json_lines: 2000
- max_report_md_lines: 800
- max_report_json_kb: 500
- max_report_md_kb: 300
- max_findings_stored: 100
- max_samples_per_rule: 10
- max_samples_per_path: 10
- max_excerpt_chars: 240
- full_raw_dump_allowed_by_default: false
- full_raw_dump_requires_owner_gate: true

## Default Behavior
- Store counts, top findings, compact samples, and omitted counters.
- Omit unlimited raw finding arrays by default.
- Keep reports as decision artifacts, not forensic archives.

## Owner Gate Requirements
- Full raw finding dump.
- Full copied source contexts.
- Any report exceeding default line/size budget.
- Commit of local raw traces into tracked repository.

## Output Policy
- Generated reports must prefer:
  - counts;
  - samples;
  - top findings;
  - omitted_findings_count;
  - explicit raw_dump_status.
- Raw trace/output must be externalized to local/private/quarantine roots unless explicitly Owner-approved for commit.

## Stop Conditions
- STOP if JSON/MD report exceeds budget and no Owner gate exists.
- STOP if scanner attempts unlimited findings dump by default.
- STOP if generated report copies source files into evidence artifact.
- STOP if recursive report scanning causes output avalanche.
