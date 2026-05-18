# Administratum-Agent V1 Hardened

Administratum-Agent V1 is the first full Organ-Agent implementation in IMPERIUM_NEW_GENERATION.
Current state is hardened toward reference-grade local execution.

Mission:
- inspect repository structure;
- classify zones/artifacts;
- build provenance index;
- detect dirty runtime outputs;
- produce useful candidate and merge-preparation intelligence;
- route findings to relevant organs;
- scan/classify IMPERIUM_CONTEXT in metadata-only mode;
- collect continuity pack and reality snapshot artifacts;
- build KPD/thinking-quality and Control Unit (цушки) summary.

Scope:
- sandbox-only (`IMPERIUM_NEW_GENERATION`);
- no canon fusion;
- no direct deletion/merge/promotion.

Runtime discipline:
- all command outputs go to `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/<run_id>/` by default;
- machine truth remains JSON/JSONL receipts and reports.

Interactive shell:
- `python IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py shell`
