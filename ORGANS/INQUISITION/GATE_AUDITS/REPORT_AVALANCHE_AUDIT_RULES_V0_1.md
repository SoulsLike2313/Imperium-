# REPORT AVALANCHE AUDIT RULES V0.1

## Attacks / Risks
- Scanner dumps all findings without compact budget controls.
- Recursive report scanning (scanner reads generated reports and explodes output).
- Report payload copies full source files into JSON/MD artifacts.
- Raw trace artifacts committed directly into repository evidence paths.
- Huge reports hide useful signal and increase false confidence.
- Oversized evidence slows future Servitor tasks and gate reviews.
- PASS/WARN semantics drowned in noise and missed by Owner review.

## Audit Blocks
- Enforce report line/size budget gates on generated artifacts.
- Require `omitted_findings_count` and `raw_dump_status` in scanner outputs.
- Require counts/samples/top-findings summary instead of full raw dumps.
- Flag any report that exceeds budget without explicit Owner gate.
- Flag scanner that includes generated report outputs as recursive scan targets.
- Block PASS when report cannot be practically reviewed due bloat.

## Minimum Evidence For PASS
- Compact JSON/MD report under configured budget thresholds.
- Explicit summary fields (severity counts, counts by rule/path, top findings).
- Declared limitations and non-claim boundaries.
- No forbidden paths touched and no runtime mutation.
