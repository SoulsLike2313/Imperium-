{\rtf1\fbidis\ansi\deff0\nouicompat{\fonttbl{\f0\fnil\fcharset0 Calibri;}{\f1\fnil Calibri;}{\f2\fnil\fcharset204 Calibri;}{\f3\fnil\fcharset1 Segoe UI Symbol;}{\f4\fnil\fcharset1 Cambria Math;}{\f5\fnil\fcharset1 Segoe UI Emoji;}}
{\*\generator Riched20 10.0.19041}{\*\mmathPr\mmathFont4\mwrapIndent1440 }\viewkind4\uc1 
\pard\sa200\sl276\slmult1\f0\fs22\lang9 # IMPERIUM \f1\emdash  \f2\lang1049\'cf\'ce\'cb\'cd\'db\'c9 \'d2\'c5\'d5\'cd\'c8\'d7\'c5\'d1\'ca\'c8\'c9 \'c0\'d3\'c4\'c8\'d2 (\'cf\'d0\'ce\'c4\'ce\'cb\'c6\'c5\'cd\'c8\'c5)\par
## \'d1\'e5\'ea\'f6\'e8\'e8 05\f1\endash 12 | \f2\'c0\'f3\'e4\'e8\'f2\'ee\'f0: Kiro | 2026-05-12\par
\par
---\par
\par
# 05. ARSENAL \'c8 SCRIPTORIUM\par
\par
## Arsenal \f1\emdash  \f2\'f0\'e5\'ea\'ee\'ec\'e5\'ed\'e4\'e0\'f6\'e8\'ff\par
\par
Arsenal = \'ea\'e0\'f2\'e0\'eb\'ee\'e3 \'e8\'ed\'f1\'f2\'f0\'f3\'ec\'e5\'ed\'f2\'ee\'e2/\'f3\'f2\'e8\'eb\'e8\'f2, \'ea\'ee\'f2\'ee\'f0\'fb\'e5 \'e0\'e3\'e5\'ed\'f2\'fb \'ec\'ee\'e3\'f3\'f2 \'e2\'fb\'e7\'fb\'e2\'e0\'f2\'fc \'e2\'ee \'e2\'f0\'e5\'ec\'ff \'f0\'e0\'e1\'ee\'f2\'fb.\par
\par
### \'c3\'e4\'e5 \'e4\'ee\'eb\'e6\'e5\'ed \'e6\'e8\'f2\'fc\par
\par
ARSENAL/ \f3\u9500?\u9472?\u9472?\f1\lang1033  \f0 ARSENAL_REGISTRY.json # \f2\lang1049\'ec\'e0\'f8\'e8\'ed\'ee\'f7\'e8\'f2\'e0\'e5\'ec\'fb\'e9 \'ea\'e0\'f2\'e0\'eb\'ee\'e3 \'e2\'f1\'e5\'f5 tools \f3\u9500?\u9472?\u9472?\f1\lang1033  \f0 README.md # \f2\lang1049\'ee\'ef\'e8\'f1\'e0\'ed\'e8\'e5 \'ea\'ee\'ed\'f6\'e5\'ef\'f6\'e8\'e8 \f3\u9500?\u9472?\u9472?\f1\lang1033  \f0 tools/ \f3\u9474?\f1  \f3\u9500?\u9472?\u9472?\f1  \f0 git_cli_check/ \f3\u9474?\f1  \f3\u9474?\f1  \f3\u9500?\u9472?\u9472?\f1  \f0 TOOL_MANIFEST.json # command_id, risk, inputs, outputs, gateway_entry \f3\u9474?\f1  \f3\u9474?\f1  \f3\u9492?\u9472?\u9472?\f1  \f0 run.py # \f2\lang1049\'e8\'eb\'e8 \'f1\'f1\'fb\'eb\'ea\'e0 \'ed\'e0 TOOLS/administratum_git_cli_check_v0_1.py \f3\u9474?\f1\lang1033  \f3\u9500?\u9472?\u9472?\f1  \f0 verify_repo/ \f3\u9474?\f1  \f3\u9474?\f1  \f3\u9500?\u9472?\u9472?\f1  \f0 TOOL_MANIFEST.json \f3\u9474?\f1  \f3\u9474?\f1  \f3\u9492?\u9472?\u9472?\f1  \f0 run.py # \f4\u8594?\f1  \f0 scripts/verify_repo.py \f3\u9474?\f1  \f3\u9500?\u9472?\u9472?\f1  \f0 build_bundle/ \f3\u9474?\f1  \f3\u9474?\f1  \f3\u9500?\u9472?\u9472?\f1  \f0 TOOL_MANIFEST.json \f3\u9474?\f1  \f3\u9474?\f1  \f3\u9492?\u9472?\u9472?\f1  \f0 run.ps1 \f3\u9474?\f1  \f3\u9492?\u9472?\u9472?\f1  \f0 transfer_prompt/ \f3\u9474?\f1  \f3\u9500?\u9472?\u9472?\f1  \f0 TOOL_MANIFEST.json \f3\u9474?\f1  \f3\u9492?\u9472?\u9472?\f1  \f0 run.py \f3\u9492?\u9472?\u9472?\f1  \f0 COMMAND_GATEWAY_MAP.json # \f2\lang1049\'ec\'e0\'ef\'ef\'e8\'ed\'e3 tool_id \f4\u8594?\f1  \f0 command_id \f2\lang1049\'e2 allowlist\par
\par
\par
### TOOL_MANIFEST.json schema\par
\par
```json\par
\{\par
  "tool_id": "verify_repo",\par
  "display_name": "Verification Spine Runner",\par
  "description": "\'c7\'e0\'ef\'f3\'f1\'ea\'e0\'e5\'f2 \'e2\'f1\'e5 verification gates \'e8 \'e3\'e5\'ed\'e5\'f0\'e8\'f0\'f3\'e5\'f2 report",\par
  "owner_organ": "MECHANICUS",\par
  "risk_level": "LOW",\par
  "command_gateway_id": "imperium.verify_repo",\par
  "inputs": [],\par
  "outputs": [".imperium_runtime/verification_spine/VERIFY_REPO_REPORT.json"],\par
  "receipt_path": ".imperium_runtime/verification_spine/VERIFY_REPO_RECEIPT.json",\par
  "safe_for_agents": true,\par
  "requires_owner_approval": false,\par
  "maturity": "operational"\par
\}\par
\'ca\'e0\'ea \'e0\'e3\'e5\'ed\'f2 \'ee\'e1\'ed\'e0\'f0\'f3\'e6\'e8\'e2\'e0\'e5\'f2 tools\par
\'d7\'e8\'f2\'e0\'e5\'f2 \par
ARSENAL_REGISTRY.json\par
\f1  \emdash  \f2\'f1\'ef\'e8\'f1\'ee\'ea \'e2\'f1\'e5\'f5 tool_id \'f1 \'ea\'f0\'e0\'f2\'ea\'e8\'ec \'ee\'ef\'e8\'f1\'e0\'ed\'e8\'e5\'ec\par
\'c4\'eb\'ff \'e4\'e5\'f2\'e0\'eb\'e5\'e9 \'f7\'e8\'f2\'e0\'e5\'f2 ARSENAL/tools/\{tool_id\}/TOOL_MANIFEST.json\par
\'c2\'fb\'e7\'fb\'e2\'e0\'e5\'f2 \'f7\'e5\'f0\'e5\'e7 command gateway: run_allowed(manifest["command_gateway_id"])\par
\'cf\'ee\'eb\'f3\'f7\'e0\'e5\'f2 receipt \'e0\'e2\'f2\'ee\'ec\'e0\'f2\'e8\'f7\'e5\'f1\'ea\'e8\par
\'ca\'e0\'ea Sanctum \'ef\'ee\'ea\'e0\'e7\'fb\'e2\'e0\'e5\'f2 Arsenal\par
\'cf\'e0\'ed\'e5\'eb\'fc "Available Tools" \f1\emdash  \f2\'f1\'ef\'e8\'f1\'ee\'ea \'e8\'e7 ARSENAL_REGISTRY.json\par
\'ca\'ed\'ee\'ef\'ea\'e0 "Run" \'e4\'eb\'ff \'ea\'e0\'e6\'e4\'ee\'e3\'ee safe tool\par
\'d1\'f2\'e0\'f2\'f3\'f1 \'ef\'ee\'f1\'eb\'e5\'e4\'ed\'e5\'e3\'ee \'e7\'e0\'ef\'f3\'f1\'ea\'e0 (\'e8\'e7 receipt)\par
\'d6\'e2\'e5\'f2\'ee\'e2\'e0\'ff \'e8\'ed\'e4\'e8\'ea\'e0\'f6\'e8\'ff risk_level\par
\'c4\'ee\'eb\'e6\'e5\'ed \'eb\'e8 Arsenal \'e1\'fb\'f2\'fc top-level?\par
\'c4\'e0. Arsenal \f1\emdash  \f2\'fd\'f2\'ee \'ee\'f2\'e4\'e5\'eb\'fc\'ed\'fb\'e9 \'e4\'ee\'ec\'e5\'ed \'ee\'f2 ORGANS, TOOLS, \'e8 src. \'cf\'f0\'e8\'f7\'e8\'ed\'fb:\par
\par
TOOLS/ \'f1\'e5\'e9\'f7\'e0\'f1 \f1\emdash  \f2\'f1\'e2\'e0\'eb\'ea\'e0 PowerShell \'f1\'ea\'f0\'e8\'ef\'f2\'ee\'e2 \'e1\'e5\'e7 \'f1\'f2\'f0\'f3\'ea\'f2\'f3\'f0\'fb\par
ORGANS/*/SCRIPTS/ \f1\emdash  organ-private \f2\'f1\'ea\'f0\'e8\'ef\'f2\'fb\par
src/ \f1\emdash  library code\par
Arsenal = \f2\'ef\'f3\'e1\'eb\'e8\'f7\'ed\'fb\'e9 \'ea\'e0\'f2\'e0\'eb\'ee\'e3 \'e2\'fb\'e7\'fb\'e2\'e0\'e5\'ec\'fb\'f5 \'e8\'ed\'f1\'f2\'f0\'f3\'ec\'e5\'ed\'f2\'ee\'e2 \'f1 \'ec\'e0\'ed\'e8\'f4\'e5\'f1\'f2\'e0\'ec\'e8\par
\'d2\'e5\'ea\'f3\'f9\'e0\'ff \'ef\'e0\'ef\'ea\'e0 TOOLS/ \'e4\'ee\'eb\'e6\'ed\'e0 \'f1\'f2\'e0\'f2\'fc source \'e4\'eb\'ff Arsenal tools, \'ed\'ee \'ed\'e5 \'e7\'e0\'ec\'e5\'ed\'ff\'f2\'fc \'e5\'e3\'ee.\par
\par
Scriptorium \f1\emdash  \f2\'f0\'e5\'ea\'ee\'ec\'e5\'ed\'e4\'e0\'f6\'e8\'ff\par
Scriptorium = \'e1\'e8\'e1\'eb\'e8\'ee\'f2\'e5\'ea\'e0 \'f1\'ea\'f0\'e8\'ef\'f2\'ee\'e2 \'f1 \'ec\'e5\'f2\'e0\'e4\'e0\'ed\'ed\'fb\'ec\'e8, \'e2\'e5\'f0\'f1\'e8\'ee\'ed\'e8\'f0\'ee\'e2\'e0\'ed\'e8\'e5\'ec \'e8 maturity tracking.\par
\par
\'cd\'f3\'e6\'e5\'ed \'eb\'e8 Scriptorium?\par
\'c4\'e0, \'ed\'ee \'ed\'e5 \'ea\'e0\'ea \'ee\'f2\'e4\'e5\'eb\'fc\'ed\'e0\'ff top-level \'ef\'e0\'ef\'ea\'e0. Scriptorium \f1\emdash  \f2\'fd\'f2\'ee \'e2\'e8\'f0\'f2\'f3\'e0\'eb\'fc\'ed\'fb\'e9 \'ea\'e0\'f2\'e0\'eb\'ee\'e3, \'ef\'ee\'f1\'f2\'f0\'ee\'e5\'ed\'ed\'fb\'e9 \'e8\'e7:\par
\par
ORGANS/*/SCRIPTS/ \f1\emdash  organ-private \f2\'f1\'ea\'f0\'e8\'ef\'f2\'fb\par
TOOLS/ \f1\emdash  shared operational \f2\'f1\'ea\'f0\'e8\'ef\'f2\'fb\par
scripts/ \f1\emdash  verification gates\par
\f2\'d1\'f2\'f0\'f3\'ea\'f2\'f3\'f0\'e0\par
REGISTRY/SCRIPTORIUM_INDEX.json   # \'e0\'e2\'f2\'ee\'e3\'e5\'ed\'e5\'f0\'e8\'f0\'f3\'e5\'ec\'fb\'e9 \'e8\'ed\'e4\'e5\'ea\'f1 \'c2\'d1\'c5\'d5 \'f1\'ea\'f0\'e8\'ef\'f2\'ee\'e2\par
SCRIPTORIUM_INDEX.json entry\par
\{\par
  "script_id": "administratum_build_continuity_pack",\par
  "path": "ORGANS/ADMINISTRATUM/SCRIPTS/administratum_build_continuity_pack.py",\par
  "owner_organ": "ADMINISTRATUM",\par
  "category": "organ_private",\par
  "maturity": "operational",\par
  "safe_to_run": true,\par
  "destructive": false,\par
  "tested": false,\par
  "has_receipt": true,\par
  "command_gateway_id": null,\par
  "description": "Builds continuity pack from current state",\par
  "last_verified": "2026-05-10"\par
\}\par
\'ca\'e0\'f2\'e5\'e3\'ee\'f0\'e8\'e8 \'f1\'ea\'f0\'e8\'ef\'f2\'ee\'e2\par
\'ca\'e0\'f2\'e5\'e3\'ee\'f0\'e8\'ff\tab\'d0\'e0\'f1\'ef\'ee\'eb\'ee\'e6\'e5\'ed\'e8\'e5\tab\'ca\'f2\'ee \'ec\'ee\'e6\'e5\'f2 \'e2\'fb\'e7\'fb\'e2\'e0\'f2\'fc\par
organ_private\tab ORGANS/*/SCRIPTS/\tab\'d2\'ee\'eb\'fc\'ea\'ee \'e2\'eb\'e0\'e4\'e5\'eb\'e5\'f6-\'ee\'f0\'e3\'e0\'ed\par
shared_operational\tab TOOLS/\tab\'cb\'fe\'e1\'ee\'e9 \'e0\'e3\'e5\'ed\'f2 \'f7\'e5\'f0\'e5\'e7 gateway\par
verification_gate\tab scripts/\tab verify_repo.py \'e0\'e3\'f0\'e5\'e3\'e0\'f2\'ee\'f0\par
training_example\tab SCRIPTORIUM/examples/ (\'e1\'f3\'e4\'f3\'f9\'e5\'e5)\tab\'d2\'ee\'eb\'fc\'ea\'ee \'e4\'eb\'ff \'ee\'e1\'f3\'f7\'e5\'ed\'e8\'ff\par
legacy_unsafe\tab\'cf\'ee\'ec\'e5\'f7\'e5\'ed\'fb "maturity": "legacy"\tab\'cd\'e8\'ea\'f2\'ee \'e1\'e5\'e7 Owner approval\par
Maturity levels\par
scaffold \f4\u8594?\f1  \f0 smoke \f4\u8594?\f1  \f0 operational \f4\u8594?\f1  \f0 production \f4\u8594?\f1  \f0 legacy \f4\u8594?\f1  \f0 deprecated\par
\f2\lang1049\'ca\'e0\'ea \'f1\'ea\'f0\'e8\'ef\'f2\'fb \'f1\'f2\'e0\'ed\'ee\'e2\'ff\'f2\'f1\'ff command-gateway \'ea\'ee\'ec\'e0\'ed\'e4\'e0\'ec\'e8\par
\'d1\'ea\'f0\'e8\'ef\'f2 \'ef\'f0\'ee\'f5\'ee\'e4\'e8\'f2 smoke test\par
\'c4\'ee\'e1\'e0\'e2\'eb\'ff\'e5\'f2\'f1\'ff \'e7\'e0\'ef\'e8\'f1\'fc \'e2 TOOL_MANIFEST.json (Arsenal)\par
\'c4\'ee\'e1\'e0\'e2\'eb\'ff\'e5\'f2\'f1\'ff command_id \'e2 COMMAND_ALLOWLIST.json\par
SCRIPTORIUM_INDEX \'ee\'e1\'ed\'ee\'e2\'eb\'ff\'e5\'f2\'f1\'ff \'f1 "command_gateway_id": "..."\par
Sanctum \'ec\'ee\'e6\'e5\'f2 \'ef\'ee\'ea\'e0\'e7\'e0\'f2\'fc \'ea\'ed\'ee\'ef\'ea\'f3 \'e7\'e0\'ef\'f3\'f1\'ea\'e0\par
\'ca\'e0\'ea \'e0\'e3\'e5\'ed\'f2\'fb \'e8\'f9\'f3\'f2 \'f1\'ea\'f0\'e8\'ef\'f2\'fb\par
# \'c2\'f1\'e5 \'f1\'ea\'f0\'e8\'ef\'f2\'fb \'ef\'ee \'ee\'f0\'e3\'e0\'ed\'f3\par
rg '"owner_organ": "ADMINISTRATUM"' REGISTRY/SCRIPTORIUM_INDEX.json\par
\par
# \'c2\'f1\'e5 \'e1\'e5\'e7\'ee\'ef\'e0\'f1\'ed\'fb\'e5 \'f1\'ea\'f0\'e8\'ef\'f2\'fb\par
python -c "import json; idx=json.load(open('REGISTRY/SCRIPTORIUM_INDEX.json')); print([s['path'] for s in idx['scripts'] if s['safe_to_run']])"\par
\par
# \'cf\'ee\'e8\'f1\'ea \'ef\'ee \'ed\'e0\'e7\'ed\'e0\'f7\'e5\'ed\'e8\'fe\par
rg "continuity|bundle|transfer" REGISTRY/SCRIPTORIUM_INDEX.json\par
06. VERIFICATION SPINE \'c8 GATES\par
\'d2\'e5\'ea\'f3\'f9\'e5\'e5 \'f1\'ee\'f1\'f2\'ee\'ff\'ed\'e8\'e5\par
\'d7\'f2\'ee \'f5\'ee\'f0\'ee\'f8\'ee\par
\'c0\'f0\'f5\'e8\'f2\'e5\'ea\'f2\'f3\'f0\'e0 \f1\emdash  5 composable gates, \f2\'e5\'e4\'e8\'ed\'fb\'e9 \'e0\'e3\'f0\'e5\'e3\'e0\'f2\'ee\'f0, structured output\par
Verdict semantics \f1\emdash  \f2\'f7\'b8\'f2\'ea\'e8\'e5 PASS/PASS_WITH_WARNINGS/FAIL/BLOCKED\par
Receipt trail \f1\emdash  \f2\'ea\'e0\'e6\'e4\'fb\'e9 \'e7\'e0\'ef\'f3\'f1\'ea \'f1\'ee\'e7\'e4\'e0\'b8\'f2 report + verdict + receipt\par
Command gateway integration \f1\emdash  gates \f2\'e8\'f1\'ef\'ee\'eb\'fc\'e7\'f3\'fe\'f2 gateway \'e4\'eb\'ff git ls-files\par
py_compile gate \f1\emdash  \f2\'eb\'ee\'e2\'e8\'f2 \'f1\'e8\'ed\'f2\'e0\'ea\'f1\'e8\'f7\'e5\'f1\'ea\'e8\'e5 \'ee\'f8\'e8\'e1\'ea\'e8 \'e2 core \'f4\'e0\'e9\'eb\'e0\'f5\par
no_raw_subprocess \f1\emdash  \f2\'f1\'ea\'e0\'ed\'e8\'f0\'f3\'e5\'f2 \'e2\'e5\'f1\'fc repo \'ed\'e0 \'ee\'e1\'f5\'ee\'e4 gateway (\'f5\'ee\'f2\'ff Sanctum \f1\emdash  approved exception)\par
\f2\'d7\'f2\'ee \'ed\'e5\'ef\'ee\'eb\'ed\'ee\par
\'cf\'f0\'ee\'e1\'eb\'e5\'ec\'e0\tab\'c2\'eb\'e8\'ff\'ed\'e8\'e5\par
121K warnings = \'f8\'f3\'ec\tab\'cd\'e5\'e2\'ee\'e7\'ec\'ee\'e6\'ed\'ee \'ee\'f2\'f1\'eb\'e5\'e6\'e8\'e2\'e0\'f2\'fc \'f0\'e5\'e3\'f0\'e5\'f1\'f1\'e8\'e8\par
\'cd\'e5\'f2 baseline/threshold\tab\'cd\'e5\'eb\'fc\'e7\'ff \'f1\'ea\'e0\'e7\'e0\'f2\'fc "\'f1\'f2\'e0\'eb\'ee \'f5\'f3\'e6\'e5"\par
Sanctum \'e2 APPROVED_FILES \'e4\'eb\'ff no_raw_subprocess\tab Security hole \'e7\'e0\'ec\'e0\'f1\'ea\'e8\'f0\'ee\'e2\'e0\'ed\'e0\par
\'cd\'e5\'f2 gate \'e4\'eb\'ff registry drift\tab ORGAN_REGISTRY \'ec\'ee\'e6\'e5\'f2 \'e2\'f0\'e0\'f2\'fc\par
\'cd\'e5\'f2 gate \'e4\'eb\'ff schema validation\tab JSON schemas \'ed\'e5 \'ef\'f0\'ee\'e2\'e5\'f0\'ff\'fe\'f2\'f1\'ff\par
\'cd\'e5\'f2 gate \'e4\'eb\'ff test pass\tab pytest \'ed\'e5 \'e2\'f5\'ee\'e4\'e8\'f2 \'e2 spine\par
\'cd\'e5\'f2 gate \'e4\'eb\'ff import health\tab Circular imports \'ed\'e5 \'eb\'ee\'e2\'ff\'f2\'f1\'ff\par
receipt_portability_check \'f1\'ea\'e0\'ed\'e8\'f0\'f3\'e5\'f2 continuity packs\tab\'ce\'f1\'ed\'ee\'e2\'ed\'ee\'e9 \'e8\'f1\'f2\'ee\'f7\'ed\'e8\'ea \'f8\'f3\'ec\'e0\par
\'d0\'e5\'ea\'ee\'ec\'e5\'ed\'e4\'f3\'e5\'ec\'fb\'e5 \'f1\'eb\'e5\'e4\'f3\'fe\'f9\'e8\'e5 gates\par
Gate ID\tab\'d7\'f2\'ee \'ef\'f0\'ee\'e2\'e5\'f0\'ff\'e5\'f2\tab\'cf\'f0\'e8\'ee\'f0\'e8\'f2\'e5\'f2\par
warning_regression\tab warnings <= baseline + 10\tab P0\par
registry_drift\tab ORGAN_REGISTRY matches ORGANS/ folders\tab P1\par
script_registry_coverage\tab\'c2\'f1\'e5 \'f1\'ea\'f0\'e8\'ef\'f2\'fb \'e2 SCRIPT_REGISTRY\tab P1\par
test_pass\tab pytest exits 0\tab P1\par
schema_validation\tab\'c2\'f1\'e5 .schema.json parseable, all referenced files valid\tab P2\par
sanctum_no_raw_subprocess\tab Sanctum uses gateway only\tab P2\par
import_health\tab All src/ imports resolve\tab P2\par
start_here_freshness\tab START_HERE.md matches HEAD\tab P3\par
Warning baseline \'ec\'e5\'f5\'e0\'ed\'e8\'e7\'ec\par
// REGISTRY/WARNING_BASELINE.json\par
\{\par
  "schema_version": "imperium.warning_baseline.v0_1",\par
  "recorded_at": "2026-05-12T09:08:52Z",\par
  "commit": "c36a8dd",\par
  "baseline_warnings": 121449,\par
  "threshold_delta": 10,\par
  "note": "Legacy debt. Must decrease over time."\par
\}\par
Gate logic:\par
\par
if current_warnings > baseline + threshold:\par
    verdict = FAIL  # regression detected\par
elif current_warnings < baseline:\par
    # auto-update baseline (improvement!)\par
    update_baseline(current_warnings)\par
    verdict = PASS\par
else:\par
    verdict = PASS_WITH_WARNINGS\par
\'ca\'e0\'ea \'ef\'f0\'e5\'e2\'f0\'e0\'f2\'e8\'f2\'fc PASS_WITH_WARNINGS \'e2 actionable queue\par
Verification report \'f3\'e6\'e5 \'f1\'ee\'e4\'e5\'f0\'e6\'e8\'f2 warnings list \'e2 \'ea\'e0\'e6\'e4\'ee\'ec gate\par
\'cd\'f3\'e6\'e5\'ed \'f1\'ea\'f0\'e8\'ef\'f2 \par
extract_warning_queue.py\par
:\par
\'d7\'e8\'f2\'e0\'e5\'f2 VERIFY_REPO_REPORT.json\par
\'c3\'f0\'f3\'ef\'ef\'e8\'f0\'f3\'e5\'f2 warnings \'ef\'ee \'f2\'e8\'ef\'f3 (absolute_path, legacy_subprocess, etc.)\par
\'c2\'fb\'e2\'ee\'e4\'e8\'f2 top-20 actionable items\par
\'c7\'e0\'ef\'e8\'f1\'fb\'e2\'e0\'e5\'f2 WARNING_QUEUE.json \'e2 runtime\par
Sanctum \'ef\'ee\'ea\'e0\'e7\'fb\'e2\'e0\'e5\'f2 Warning Queue \'ef\'e0\'ed\'e5\'eb\'fc \'f1 \'ea\'ed\'ee\'ef\'ea\'ee\'e9 "Fix Next"\par
CI \'ef\'eb\'e0\'ed\par
# .github/workflows/verify.yml\par
name: IMPERIUM Verification Spine\par
on: [push, pull_request]\par
jobs:\par
  verify:\par
    runs-on: ubuntu-latest\par
    steps:\par
      - uses: actions/checkout@v4\par
      - uses: actions/setup-python@v5\par
        with: \{python-version: '3.12'\}\par
      - run: pip install -e ".[dev]"\par
      - run: python scripts/verify_repo.py\par
      - run: python -m pytest tests/ -q\par
      - name: Check no regression\par
        run: |\par
          WARNINGS=$(python -c "import json; r=json.load(open('.imperium_runtime/verification_spine/VERIFY_REPO_REPORT.json')); print(r['counts']['warnings'])")\par
          BASELINE=$(python -c "import json; b=json.load(open('REGISTRY/WARNING_BASELINE.json')); print(b['baseline_warnings'])")\par
          if [ "$WARNINGS" -gt "$((BASELINE + 10))" ]; then exit 1; fi\par
07. TASK LIFECYCLE \'c8 AGENT ORCHESTRATION\par
\'d2\'e5\'ea\'f3\'f9\'e5\'e5 \'f1\'ee\'f1\'f2\'ee\'ff\'ed\'e8\'e5\par
Task lifecycle \'e4\'ee\'ea\'f3\'ec\'e5\'ed\'f2\'e8\'f0\'ee\'e2\'e0\'ed \'e2 \par
TASK_LIFECYCLE_V0_1.md\par
 \'ed\'ee \'ed\'e5 \'e8\'ec\'e5\'e5\'f2 \'e8\'f1\'ef\'ee\'eb\'ed\'ff\'e5\'ec\'ee\'e3\'ee \'ea\'ee\'e4\'e0. \'d1\'f3\'f9\'e5\'f1\'f2\'e2\'f3\'fe\'f2:\par
\par
Smoke-\'f1\'ea\'f0\'e8\'ef\'f2\'fb \'e2 TOOLS/ (preflight, work_packet, stage_result) \f1\emdash  \f2\'ed\'ee \'fd\'f2\'ee \'e7\'e0\'e3\'eb\'f3\'f8\'ea\'e8 \'e4\'eb\'ff E2E demo\par
Astronomicon task records \f1\emdash  \f2\'ed\'ee \'fd\'f2\'ee \'f1\'f2\'e0\'f2\'e8\'f7\'e5\'f1\'ea\'e8\'e5 JSON, \'ed\'e5 runtime\par
Administratum memory spine \f1\emdash  \f2\'ed\'ee \'fd\'f2\'ee event log, \'ed\'e5 orchestrator\par
\'d0\'e5\'ea\'ee\'ec\'e5\'ed\'e4\'f3\'e5\'ec\'fb\'e9 \'ef\'f0\'e0\'ea\'f2\'e8\'f7\'e5\'f1\'ea\'e8\'e9 task flow\par
\f3\u9484?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9488?\f0\lang1033\par
\f3\u9474?\f1  \f0 OWNER INPUT                                                      \f3\u9474?\f0\par
\f3\u9474?\f1  \f0 "\f2\lang1049\'cf\'ee\'f1\'f2\'f0\'ee\'e8\'f2\'fc portfolio website"                                    \f3\u9474?\f0\lang1033\par
\f3\u9492?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9516?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9496?\f0\par
\f1                        \f3\u9660?\f0\par
\f3\u9484?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9488?\f0\par
\f3\u9474?\f1  \f0 1. STRATEGIUM: scope_and_plan()                                  \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Input: owner goal text                                        \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Output: TASK_BRIEF.json (scope, constraints, success criteria)\f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Executor: PC agent / Kiro / Claude                            \f3\u9474?\f0\par
\f3\u9492?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9516?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9496?\f0\par
\f1                        \f3\u9660?\f0\par
\f3\u9484?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9488?\f0\par
\f3\u9474?\f1  \f0 2. DOCTRINARIUM: preflight_check()                               \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Input: TASK_BRIEF.json                                        \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Output: PREFLIGHT_RECEIPT.json (laws checked, health ok)      \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Executor: automated (Python script)                           \f3\u9474?\f0\par
\f3\u9492?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9516?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9496?\f0\par
\f1                        \f3\u9660?\f0\par
\f3\u9484?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9488?\f0\par
\f3\u9474?\f1  \f0 3. OFFICIO AGENTIS: assign_agent()                               \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Input: task complexity, available agents                       \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Output: AGENT_SCOPE.json (who does what)                      \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Executor: automated or Owner decision                         \f3\u9474?\f0\par
\f3\u9492?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9516?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9496?\f0\par
\f1                        \f3\u9660?\f0\par
\f3\u9484?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9488?\f0\par
\f3\u9474?\f1  \f0 4. ADMINISTRATUM: register_task() + issue_work_packet()          \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Input: TASK_BRIEF + AGENT_SCOPE                               \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Output: TASK_LAUNCH_CARD.json + WORK_PACKET.json              \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Executor: automated                                           \f3\u9474?\f0\par
\f3\u9492?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9516?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9496?\f0\par
\f1                        \f3\u9660?\f0\par
\f3\u9484?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9488?\f0\par
\f3\u9474?\f1  \f0 5. ASTRONOMICON: decompose_to_stages()                           \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Input: WORK_PACKET.json                                       \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Output: STAGE_MAP.json (ordered stages with dependencies)     \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Executor: PC agent / automated                                \f3\u9474?\f0\par
\f3\u9492?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9516?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9496?\f0\par
\f1                        \f3\u9660?\f0\par
\f3\u9484?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9488?\f0\par
\f3\u9474?\f1  \f0 6. MECHANICUS: resolve_tools()                                   \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Input: STAGE_MAP.json                                         \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Output: TOOL_SELECTION.json (scripts per stage)               \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Executor: automated                                           \f3\u9474?\f0\par
\f3\u9492?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9516?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9496?\f0\par
\f1                        \f3\u9660?\f0\par
\f3\u9484?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9488?\f0\par
\f3\u9474?\f1  \f0 7. EXECUTION LOOP (per stage):                                   \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 a. Agent receives work packet for stage                       \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 b. Agent executes (code, research, build)                     \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 c. Agent produces STAGE_RESULT.json + artifacts               \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 d. INQUISITION: audit_stage_result() \f4\u8594?\f1  \f0 AUDIT_RECEIPT.json     \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 e. If FAIL \f4\u8594?\f1  \f0 back to agent or escalate to Owner               \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 f. If PASS \f4\u8594?\f1  \f0 next stage                                       \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Executor: PC / VM2 / external Kiro / Claude / browser agent   \f3\u9474?\f0\par
\f3\u9492?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9516?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9496?\f0\par
\f1                        \f3\u9660?\f0\par
\f3\u9484?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9488?\f0\par
\f3\u9474?\f1  \f0 8. ADMINISTRATUM: register_completion()                          \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Input: all stage results + audit receipts                     \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Output: TASK_COMPLETION_RECORD.json                           \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Executor: automated                                           \f3\u9474?\f0\par
\f3\u9492?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9516?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9496?\f0\par
\f1                        \f3\u9660?\f0\par
\f3\u9484?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9488?\f0\par
\f3\u9474?\f1  \f0 9. SCHOLA IMPERIALIS: record_lessons()                           \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Input: task history, failures, fixes, patterns                 \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Output: LESSON_RECORD.json (searchable knowledge)             \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Executor: PC agent / automated extraction                     \f3\u9474?\f0\par
\f3\u9492?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9516?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9496?\f0\par
\f1                        \f3\u9660?\f0\par
\f3\u9484?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9488?\f0\par
\f3\u9474?\f1  \f0 10. THRONE: owner_acceptance()                                   \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Input: TASK_COMPLETION_RECORD + artifacts                     \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Output: ACCEPTANCE_VERDICT.json (ACCEPTED / REJECTED / REDO)  \f3\u9474?\f0\par
\f3\u9474?\f1     \f0 Executor: Owner only                                          \f3\u9474?\f0\par
\f3\u9492?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9472?\u9496?\f0\par
\f2\lang1049\'ca\'e0\'ea \'f0\'e0\'e7\'ed\'fb\'e5 executors \'e2\'e7\'e0\'e8\'ec\'ee\'e4\'e5\'e9\'f1\'f2\'e2\'f3\'fe\'f2\par
Executor\tab\'cf\'ee\'eb\'f3\'f7\'e0\'e5\'f2 \'e7\'e0\'e4\'e0\'f7\'f3 \'f7\'e5\'f0\'e5\'e7\tab\'ce\'f2\'e4\'e0\'b8\'f2 \'f0\'e5\'e7\'f3\'eb\'fc\'f2\'e0\'f2 \'f7\'e5\'f0\'e5\'e7\tab\'ce\'e3\'f0\'e0\'ed\'e8\'f7\'e5\'ed\'e8\'ff\par
PC Kiro/Claude\tab\'cf\'f0\'ff\'ec\'ee\'e9 \'e4\'ee\'f1\'f2\'f3\'ef \'ea repo\tab git commit + receipt\tab\'cf\'ee\'eb\'ed\'fb\'e9 \'e4\'ee\'f1\'f2\'f3\'ef \'ea src\par
VM2 agent\tab Prompt file (SCP)\tab Bundle ZIP (SCP back)\tab\'c8\'e7\'ee\'eb\'e8\'f0\'ee\'e2\'e0\'ed, \'ed\'e5\'f2 git push\par
External Kiro\tab GitHub clone + bundle\tab PR \'e8\'eb\'e8 patch bundle\tab Read-only \'ea private\par
Browser/Playwright\tab Task URL + instructions\tab Screenshot + JSON result\tab\'cd\'e5\'f2 \'e4\'ee\'f1\'f2\'f3\'ef\'e0 \'ea repo\par
Future cloud LLM\tab API call + context\tab JSON response\tab Stateless, \'ed\'e5\'f2 \'f4\'e0\'e9\'eb\'ee\'e2\par
Owner\tab Sanctum UI\tab Click Accept/Reject\tab Final authority\par
\'d7\'f2\'ee \'ee\'f2\'f1\'f3\'f2\'f1\'f2\'e2\'f3\'e5\'f2 \'e2 \'ea\'ee\'e4\'e5\par
Orchestrator script \f1\emdash  \f2\'ed\'e5\'f2 imperium_run_task.py \'ea\'ee\'f2\'ee\'f0\'fb\'e9 \'e1\'fb \'ef\'f0\'ee\'e3\'ee\'ed\'ff\'eb pipeline\par
Stage state machine \f1\emdash  \f2\'ed\'e5\'f2 \'ea\'ee\'e4\'e0 \'e4\'eb\'ff PLANNED \f4\u8594?\f1  \f0 ACTIVE \f4\u8594?\f1  \f0 PASS/FAIL transitions\par
Agent dispatch \f1\emdash  \f2\lang1049\'ed\'e5\'f2 \'ea\'ee\'e4\'e0 \'e4\'eb\'ff \'e2\'fb\'e1\'ee\'f0\'e0 \'e8 \'ee\'f2\'ef\'f0\'e0\'e2\'ea\'e8 \'e7\'e0\'e4\'e0\'f7\'e8 \'e0\'e3\'e5\'ed\'f2\'f3\par
Lesson extraction \f1\emdash  \f2\'ed\'e5\'f2 \'ea\'ee\'e4\'e0 \'e4\'eb\'ff Schola\par
Owner acceptance UI \f1\emdash  \f2\'ed\'e5\'f2 \'ea\'ed\'ee\'ef\'ea\'e8 \'e2 Sanctum \'e4\'eb\'ff Accept/Reject\par
08. \'c1\'c5\'c7\'ce\'cf\'c0\'d1\'cd\'ce\'d1\'d2\'dc \'c8 \'c3\'d0\'c0\'cd\'c8\'d6\'db\par
Public/Private boundary\par
\'c7\'ee\'ed\'e0\tab\'d1\'f2\'e0\'f2\'f3\'f1\tab\'d0\'e8\'f1\'ea\par
GitHub repo (public)\tab\'d7\'e8\'f1\'f2\'fb\'e9 \f1\emdash  \f2\'ed\'e5\'f2 \'f1\'e5\'ea\'f0\'e5\'f2\'ee\'e2 \'e2 tracked files\tab LOW\par
.gitignore\tab\'d5\'ee\'f0\'ee\'f8\'ee \'ed\'e0\'f1\'f2\'f0\'ee\'e5\'ed \f1\emdash  .pem, .key, credentials, secrets\tab LOW\par
SSH key path \f2\'e2 \'ea\'ee\'e4\'e5\tab\'d2\'ee\'eb\'fc\'ea\'ee path, \'ed\'e5 material: ~/.ssh/imperium_pc_to_vm2_ed25519_20260418\tab MEDIUM\par
VM2 paths \'e2 \'ea\'ee\'e4\'e5\tab /home/vboxuser2/IMPERIUM_PRIVATE/WORKDROP \f1\emdash  \f2\'f0\'e0\'f1\'ea\'f0\'fb\'e2\'e0\'e5\'f2 \'f1\'f2\'f0\'f3\'ea\'f2\'f3\'f0\'f3\tab LOW\par
Absolute Windows paths\tab E:\\IMPERIUM \'e2 10+ \'f4\'e0\'e9\'eb\'e0\'f5 \f1\emdash  \f2\'f0\'e0\'f1\'ea\'f0\'fb\'e2\'e0\'e5\'f2 local structure\tab LOW\par
Continuity packs\tab\'d1\'ee\'e4\'e5\'f0\'e6\'e0\'f2 system state snapshots \f1\emdash  \f2\'ef\'ee\'f2\'e5\'ed\'f6\'e8\'e0\'eb\'fc\'ed\'ee sensitive\tab MEDIUM\par
\'ca\'ee\'ed\'ea\'f0\'e5\'f2\'ed\'fb\'e5 \'ed\'e0\'f5\'ee\'e4\'ea\'e8\par
\'d1\'e5\'ea\'f0\'e5\'f2\'fb\par
\'cd\'e5\'f2 \'f3\'f2\'e5\'f7\'e5\'ea \'f1\'e5\'ea\'f0\'e5\'f2\'ee\'e2. public_private_boundary_scan gate \'f0\'e0\'e1\'ee\'f2\'e0\'e5\'f2. \'cd\'e5\'f2 private keys, tokens, passwords \'e2 tracked files.\par
SSH key path \'ef\'f0\'e8\'f1\'f3\'f2\'f1\'f2\'e2\'f3\'e5\'f2 (\'ed\'e5 material) \f1\emdash  \f2\'fd\'f2\'ee acceptable \'ef\'ee \'f2\'e5\'ea\'f3\'f9\'e5\'e9 policy.\par
Screenshots\par
SANCTUM/SCREENSHOTS/ \'e8 ORGANS/DOCTRINARIUM/UTILITY/PLAYWRIGHT_AUDIT*/screenshots/ \f1\emdash  \f2\'f1\'ee\'e4\'e5\'f0\'e6\'e0\'f2 PNG \'f1\'ea\'f0\'e8\'ed\'f8\'ee\'f2\'fb \'e4\'e0\'f8\'e1\'ee\'f0\'e4\'ee\'e2. \'cd\'e5 \'f1\'ee\'e4\'e5\'f0\'e6\'e0\'f2 sensitive data (\'ef\'f0\'ee\'e2\'e5\'f0\'e5\'ed\'ee \'ef\'ee \'e8\'ec\'e5\'ed\'e0\'ec \'f4\'e0\'e9\'eb\'ee\'e2).\par
\'d0\'e8\'f1\'ea: \'c5\'f1\'eb\'e8 \'e4\'e0\'f8\'e1\'ee\'f0\'e4 \'ea\'ee\'e3\'e4\'e0-\'ed\'e8\'e1\'f3\'e4\'fc \'ef\'ee\'ea\'e0\'e6\'e5\'f2 secrets, \'f1\'ea\'f0\'e8\'ed\'f8\'ee\'f2\'fb \'f3\'f2\'e5\'ea\'f3\'f2 \'e2 Git.\par
Fix: \'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc gate: "no screenshots with sensitive content" (manual review marker).\par
Bundles\par
.imperium_runtime/bundles/ \f1\emdash  \f2\'e2 .gitignore, \'ef\'f0\'e0\'e2\'e8\'eb\'fc\'ed\'ee.\par
ARTIFACTS/**/*.zip \f1\emdash  \f2\'e2 .gitignore, \'ef\'f0\'e0\'e2\'e8\'eb\'fc\'ed\'ee.\par
\'d0\'e8\'f1\'ea: \'c5\'f1\'eb\'e8 \'ea\'f2\'ee-\'f2\'ee \'e2\'f0\'f3\'f7\'ed\'f3\'fe git add bundle \f1\emdash  \f2\'ee\'ed \'ef\'ee\'ef\'e0\'e4\'b8\'f2 \'e2 public repo.\par
Fix: \'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc pre-commit hook: reject files > 1MB.\par
Command execution\par
Command gateway \f1\emdash  \f2\'e5\'e4\'e8\'ed\'f1\'f2\'e2\'e5\'ed\'ed\'e0\'ff approved \'f2\'ee\'f7\'ea\'e0 subprocess. \'d5\'ee\'f0\'ee\'f8\'ee.\par
\'cd\'ee: Sanctum, GitCliCheckService, \'e8 TOOLS/*.py \'ee\'e1\'f5\'ee\'e4\'ff\'f2 gateway. \'dd\'f2\'ee 3 \'e4\'fb\'f0\'fb.\par
Fix: \'c2\'f1\'e5 subprocess \'e2\'fb\'e7\'ee\'e2\'fb \'e4\'ee\'eb\'e6\'ed\'fb \'e8\'e4\'f2\'e8 \'f7\'e5\'f0\'e5\'e7 gateway. Sanctum \f1\emdash  \f2\'ef\'e5\'f0\'e2\'fb\'e9 \'ef\'f0\'e8\'ee\'f0\'e8\'f2\'e5\'f2.\par
VM boundaries\par
VM2 \'e4\'ee\'f1\'f2\'f3\'ef \'f7\'e5\'f0\'e5\'e7 SSH \'f1 key auth \f1\emdash  \f2\'ef\'f0\'e0\'e2\'e8\'eb\'fc\'ed\'ee.\par
VM2 \'ed\'e5 \'e8\'ec\'e5\'e5\'f2 push access \'ea GitHub \f1\emdash  \f2\'ef\'f0\'e0\'e2\'e8\'eb\'fc\'ed\'ee.\par
VM2 \'ef\'ee\'eb\'f3\'f7\'e0\'e5\'f2 \'f2\'ee\'eb\'fc\'ea\'ee prompt files \'e8 \'ee\'f2\'e4\'e0\'b8\'f2 bundles \f1\emdash  \f2\'ef\'f0\'e0\'e2\'e8\'eb\'fc\'ed\'e0\'ff \'e8\'e7\'ee\'eb\'ff\'f6\'e8\'ff.\par
\'d0\'e8\'f1\'ea: \'c5\'f1\'eb\'e8 prompt \'f1\'ee\'e4\'e5\'f0\'e6\'e8\'f2 secrets \f1\emdash  \f2\'ee\'ed\'e8 \'ee\'ea\'e0\'e6\'f3\'f2\'f1\'ff \'ed\'e0 VM2 \'e1\'e5\'e7 \'ea\'ee\'ed\'f2\'f0\'ee\'eb\'ff.\par
Fix: \'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc scan prompt text \'ef\'e5\'f0\'e5\'e4 \'ee\'f2\'ef\'f0\'e0\'e2\'ea\'ee\'e9 (reuse public_private_boundary_scan logic).\par
GitHub/public repo leakage risk\par
\'c2\'e5\'ea\'f2\'ee\'f0\tab\'d2\'e5\'ea\'f3\'f9\'e0\'ff \'e7\'e0\'f9\'e8\'f2\'e0\tab\'c4\'ee\'f1\'f2\'e0\'f2\'ee\'f7\'ed\'ee?\par
Secrets \'e2 \'ea\'ee\'e4\'e5\tab public_private_boundary_scan gate\tab\f3\u9989?\f1\lang1033  \f2\lang1049\'c4\'e0\par
Large binaries\tab .gitignore \'e4\'eb\'ff .zip\tab\f5\u9888?\u-497?\f1\lang1033  \f2\lang1049\'cd\'e5\'f2 pre-commit hook\par
Screenshots \'f1 sensitive\tab\'cd\'e5\'f2 \'e7\'e0\'f9\'e8\'f2\'fb\tab\f3\u10060?\f1\lang1033  \f2\lang1049\'cd\'e5\'f2\par
Continuity packs \'f1 paths\tab\'c2 Git-\'f2\'f0\'e5\'ea\'e8\'ed\'e3\'e5!\tab\f3\u10060?\f1\lang1033  \f2\lang1049\'cd\'e5\'f2 \f1\emdash  \f2\'ee\'f1\'ed\'ee\'e2\'ed\'ee\'e9 \'f0\'e8\'f1\'ea\par
Prompt text \'f1 secrets\tab\'cd\'e5\'f2 scan \'ef\'e5\'f0\'e5\'e4 send\tab\f5\u9888?\u-497?\f1\lang1033  \f2\lang1049\'d1\'f0\'e5\'e4\'ed\'e8\'e9 \'f0\'e8\'f1\'ea\par
09. ROADMAP\par
\'d1\'eb\'e5\'e4\'f3\'fe\'f9\'e8\'e5 24 \'f7\'e0\'f1\'e0\par
#\tab\'c7\'e0\'e4\'e0\'f7\'e0\tab\'cf\'ee\'f7\'e5\'ec\'f3\tab\'d4\'e0\'e9\'eb\'fb\tab\'ce\'f0\'e3\'e0\'ed\tab Executor\tab\'c2\'e0\'eb\'e8\'e4\'e0\'f6\'e8\'ff\par
1\tab\'d1\'ee\'e7\'e4\'e0\'f2\'fc AGENTS.md\tab\'c0\'e3\'e5\'ed\'f2\'fb \'ed\'e5 \'ec\'ee\'e3\'f3\'f2 \'ed\'e0\'e2\'e8\'e3\'e8\'f0\'ee\'e2\'e0\'f2\'fc\tab AGENTS.md (\'ed\'ee\'e2\'fb\'e9)\tab Administratum\tab PC agent\tab\'d4\'e0\'e9\'eb \'f1\'f3\'f9\'e5\'f1\'f2\'e2\'f3\'e5\'f2, \'f1\'ee\'e4\'e5\'f0\'e6\'e8\'f2 SAFE_COMMANDS \'f1\'e5\'ea\'f6\'e8\'fe\par
2\tab\'d3\'e1\'f0\'e0\'f2\'fc continuity packs \'e8\'e7 Git\tab 121K warnings, repo bloat\tab .gitignore, git rm --cached\tab Administratum\tab Owner + PC\tab git ls-files ORGANS/ADMINISTRATUM/CONTINUITY/PACKS/ | wc -l = 0\par
3\tab\'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc WARNING_BASELINE.json\tab\'c1\'e5\'e7 baseline \'ed\'e5\'eb\'fc\'e7\'ff \'eb\'ee\'e2\'e8\'f2\'fc \'f0\'e5\'e3\'f0\'e5\'f1\'f1\'e8\'e8\tab\par
WARNING_BASELINE.json\par
Inquisition\tab PC agent\tab\'d4\'e0\'e9\'eb \'f1\'f3\'f9\'e5\'f1\'f2\'e2\'f3\'e5\'f2 \'f1 \'f2\'e5\'ea\'f3\'f9\'e8\'ec count\par
4\tab\'ce\'e1\'ed\'ee\'e2\'e8\'f2\'fc ORGAN_REGISTRY\tab Registry drift\tab\par
ORGAN_REGISTRY.json\par
Administratum\tab PC agent\tab\'c2\'f1\'e5 6 \'f1\'f3\'f9\'e5\'f1\'f2\'e2\'f3\'fe\'f9\'e8\'f5 \'ee\'f0\'e3\'e0\'ed\'ee\'e2 \'e2 registry\par
\'d1\'eb\'e5\'e4\'f3\'fe\'f9\'e8\'e5 48 \'f7\'e0\'f1\'ee\'e2\par
#\tab\'c7\'e0\'e4\'e0\'f7\'e0\tab\'cf\'ee\'f7\'e5\'ec\'f3\tab\'d4\'e0\'e9\'eb\'fb\tab\'ce\'f0\'e3\'e0\'ed\tab Executor\tab\'c2\'e0\'eb\'e8\'e4\'e0\'f6\'e8\'ff\par
5\tab\'c0\'f0\'f5\'e8\'e2\'e8\'f0\'ee\'e2\'e0\'f2\'fc Sanctum v0.1\f1\endash v0.28\tab Dead code noise\tab SANCTUM/ARCHIVE/\tab Mechanicus\tab PC agent\tab git ls-files SANCTUM/sanctum_v0_[0-2][0-8]*.py = 0\par
6\tab\f2\'d3\'e1\'f0\'e0\'f2\'fc \'f5\'e0\'f0\'e4\'ea\'ee\'e4 E:\\IMPERIUM \'e8\'e7 Sanctum\tab\'cf\'ee\'f0\'f2\'e8\'f0\'f3\'e5\'ec\'ee\'f1\'f2\'fc\tab\par
sanctum_v0_29_qt.py\par
Mechanicus\tab PC agent\tab rg 'E:\\\\\\\\IMPERIUM' SANCTUM/sanctum_v0_29_qt.py = 0\par
7\tab\'d1\'ee\'e7\'e4\'e0\'f2\'fc scaffold \'e4\'eb\'ff 4 missing organs\tab Task lifecycle completeness\tab ORGANS/CUSTODES/, ORGANS/STRATEGIUM/, ORGANS/SCHOLA_IMPERIALIS/, ORGANS/THRONE/\tab Doctrinarium\tab PC agent\tab\'c2\'f1\'e5 4 \'e8\'ec\'e5\'fe\'f2 ORGAN_STATUS.json\par
8\tab\'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc CI workflow\tab\'c0\'e2\'f2\'ee\'ec\'e0\'f2\'e8\'f7\'e5\'f1\'ea\'e0\'ff \'e2\'e5\'f0\'e8\'f4\'e8\'ea\'e0\'f6\'e8\'ff\tab\par
verify.yml\par
Mechanicus\tab PC agent\tab Push \'f2\'f0\'e8\'e3\'e3\'e5\'f0\'e8\'f2 CI\par
\'d1\'eb\'e5\'e4\'f3\'fe\'f9\'e0\'ff \'ed\'e5\'e4\'e5\'eb\'ff\par
#\tab\'c7\'e0\'e4\'e0\'f7\'e0\tab\'cf\'ee\'f7\'e5\'ec\'f3\tab\'d4\'e0\'e9\'eb\'fb\tab\'ce\'f0\'e3\'e0\'ed\tab Executor\tab\'c2\'e0\'eb\'e8\'e4\'e0\'f6\'e8\'ff\par
9\tab\'cf\'e5\'f0\'e5\'ef\'e8\'f1\'e0\'f2\'fc Sanctum TransferService \'ed\'e0 gateway\tab Security boundary\tab\par
sanctum_v0_29_qt.py\par
, \par
COMMAND_ALLOWLIST.json\par
Mechanicus\tab PC agent\tab rg "subprocess" SANCTUM/sanctum_v0_29_qt.py = \'f2\'ee\'eb\'fc\'ea\'ee import\par
10\tab\'d0\'e0\'e7\'e1\'e8\'f2\'fc Sanctum \'ed\'e0 \'ec\'ee\'e4\'f3\'eb\'e8\tab Maintainability\tab SANCTUM/widgets/, SANCTUM/services/\tab Mechanicus\tab PC agent\tab sanctum_v0_29_qt.py < 200 \'f1\'f2\'f0\'ee\'ea\par
11\tab\'c0\'e2\'f2\'ee\'e3\'e5\'ed\'e5\'f0\'e0\'f6\'e8\'ff SCRIPTORIUM_INDEX\tab Agent discoverability\tab\par
SCRIPTORIUM_INDEX.json\par
, \'f1\'ea\'f0\'e8\'ef\'f2 \'e3\'e5\'ed\'e5\'f0\'e0\'f6\'e8\'e8\tab Mechanicus\tab PC agent\tab\'c2\'f1\'e5 .py/.ps1 \'e2 TOOLS/ \'e8 ORGANS/*/SCRIPTS/ \'ef\'ee\'ea\'f0\'fb\'f2\'fb\par
12\tab\'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc gate warning_regression\tab\'cb\'ee\'e2\'e8\'f2\'fc \'f3\'f5\'f3\'e4\'f8\'e5\'ed\'e8\'ff\tab\par
warning_regression.py\par
Inquisition\tab PC agent\tab Gate \'e2 verify_repo.py\par
13\tab\'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc gate registry_drift\tab Registry accuracy\tab\par
registry_drift_check.py\par
Inquisition\tab PC agent\tab Gate \'e2 verify_repo.py\par
14\tab Verification panel \'e2 Sanctum\tab Visibility\tab\par
verification_panel.py\par
Mechanicus\tab PC agent\tab Sanctum \'ef\'ee\'ea\'e0\'e7\'fb\'e2\'e0\'e5\'f2 gate results\par
15\tab\'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc ruff/mypy\tab Code quality\tab pyproject.toml\tab Mechanicus\tab PC agent\tab ruff check src/ scripts/ = 0 errors\par
\'d1\'eb\'e5\'e4\'f3\'fe\'f9\'e8\'e9 \'ec\'e5\'f1\'ff\'f6\par
#\tab\'c7\'e0\'e4\'e0\'f7\'e0\tab\'cf\'ee\'f7\'e5\'ec\'f3\tab\'ce\'f0\'e3\'e0\'ed\tab Executor\par
16\tab\'d0\'e5\'e0\'eb\'e8\'e7\'ee\'e2\'e0\'f2\'fc task orchestrator MVP\tab Core value prop\tab Administratum + Astronomicon\tab PC + VM2\par
17\tab Arsenal v0.1 \'f1 5 tools\tab Agent tool discovery\tab Mechanicus\tab PC agent\par
18\tab Schola lessons extraction\tab Learning from tasks\tab Schola Imperialis\tab PC agent\par
19\tab Owner acceptance UI \'e2 Sanctum\tab Throne functionality\tab Throne + Mechanicus\tab PC agent\par
20\tab Browser/Playwright agent integration\tab Expand executor types\tab Officio Agentis\tab PC + VM2\par
21\tab Sanctum organ launch buttons\tab Control room completeness\tab Mechanicus\tab PC agent\par
22\tab Pre-commit hooks\tab Prevent leaks\tab Custodes\tab PC agent\par
\'cf\'ee\'e7\'e6\'e5\par
#\tab\'c7\'e0\'e4\'e0\'f7\'e0\tab\'cf\'ee\'f7\'e5\'ec\'f3\par
23\tab Cloud LLM integration (free tier)\tab Expand compute\par
24\tab Multi-agent coordination protocol\tab Parallel execution\par
25\tab Sanctum web version (remote access)\tab VM2/mobile access\par
26\tab Auto-generated documentation from receipts\tab Knowledge base\par
27\tab Performance metrics dashboard\tab Operational speed tracking\par
10. FINDINGS.YAML\par
\par
findings:\par
  - id: TH-001\par
    title: "Sanctum \'ee\'e1\'f5\'ee\'e4\'e8\'f2 Command Gateway \'f7\'e5\'f0\'e5\'e7 raw subprocess"\par
    severity: BLOCKER\par
    area: security\par
    evidence_paths:\par
      - SANCTUM/sanctum_v0_29_qt.py\par
      - SANCTUM/sanctum_v0_28.py\par
    problem: "subprocess.run \'e8 subprocess.Popen \'e2\'fb\'e7\'fb\'e2\'e0\'fe\'f2\'f1\'ff \'ed\'e0\'ef\'f0\'ff\'ec\'f3\'fe, \'ec\'e8\'ed\'f3\'ff command_gateway.run_allowed()"\par
    operational_impact: "\'cd\'e5\'f2 audit trail \'e4\'eb\'ff SSH/SCP \'ee\'ef\'e5\'f0\'e0\'f6\'e8\'e9. Security boundary \'e1\'e5\'f1\'f1\'ec\'fb\'f1\'eb\'e5\'ed\'ed\'e0."\par
    recommended_fix: "\'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc SSH/SCP \'e2 COMMAND_ALLOWLIST. \'cf\'e5\'f0\'e5\'ef\'e8\'f1\'e0\'f2\'fc TransferService \'ed\'e0 gateway."\par
    acceptance_gate: "rg -n 'subprocess\\\\.(run|Popen)' SANCTUM/sanctum_v0_29_qt.py \'e2\'ee\'e7\'e2\'f0\'e0\'f9\'e0\'e5\'f2 0"\par
    responsible_organs: [MECHANICUS, INQUISITION]\par
    suggested_task_id: TASK-20260513-SANCTUM-GATEWAY-MIGRATION\par
\par
  - id: TH-002\par
    title: "121K warnings \'e4\'e5\'eb\'e0\'fe\'f2 verification \'e1\'e5\'f1\'ef\'ee\'eb\'e5\'e7\'ed\'ee\'e9"\par
    severity: BLOCKER\par
    area: verification\par
    evidence_paths:\par
      - .imperium_runtime/verification_spine/VERIFY_REPO_REPORT.json\par
      - ORGANS/ADMINISTRATUM/CONTINUITY/PACKS/\par
    problem: "121449 warnings \'e2 \'ee\'f1\'ed\'ee\'e2\'ed\'ee\'ec \'ee\'f2 absolute paths \'e2 continuity packs"\par
    operational_impact: "\'cd\'e5\'e2\'ee\'e7\'ec\'ee\'e6\'ed\'ee \'ee\'f2\'eb\'e8\'f7\'e8\'f2\'fc \'ed\'ee\'e2\'fb\'e9 warning \'ee\'f2 legacy \'f8\'f3\'ec\'e0"\par
    recommended_fix: "\'d3\'e1\'f0\'e0\'f2\'fc continuity packs \'e8\'e7 Git. \'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc WARNING_BASELINE.json."\par
    acceptance_gate: "python scripts/verify_repo.py \'ef\'ee\'ea\'e0\'e7\'fb\'e2\'e0\'e5\'f2 warnings < 100"\par
    responsible_organs: [ADMINISTRATUM, INQUISITION]\par
    suggested_task_id: TASK-20260512-WARNING-FLOOD-FIX\par
\par
  - id: TH-003\par
    title: "\'cd\'e5\'f2 \'ec\'e0\'f8\'e8\'ed\'ee\'f7\'e8\'f2\'e0\'e5\'ec\'ee\'e9 \'f2\'ee\'f7\'ea\'e8 \'e2\'f5\'ee\'e4\'e0 \'e4\'eb\'ff \'e0\'e3\'e5\'ed\'f2\'ee\'e2"\par
    severity: BLOCKER\par
    area: navigation\par
    evidence_paths:\par
      - README.md\par
      - START_HERE.md\par
    problem: "\'cd\'e5\'f2 AGENTS.md \'f1 safe commands, active/legacy zones, verify command"\par
    operational_impact: "\'ca\'e0\'e6\'e4\'fb\'e9 \'e0\'e3\'e5\'ed\'f2 \'f2\'f0\'e0\'f2\'e8\'f2 5-10 \'ec\'e8\'ed\'f3\'f2 \'ed\'e0 \'ee\'f0\'e8\'e5\'ed\'f2\'e0\'f6\'e8\'fe"\par
    recommended_fix: "\'d1\'ee\'e7\'e4\'e0\'f2\'fc AGENTS.md \'f1 \'f1\'e5\'ea\'f6\'e8\'ff\'ec\'e8 SAFE_COMMANDS, ACTIVE_SOURCE, LEGACY_ZONES"\par
    acceptance_gate: "\'d4\'e0\'e9\'eb AGENTS.md \'f1\'f3\'f9\'e5\'f1\'f2\'e2\'f3\'e5\'f2 \'e2 \'ea\'ee\'f0\'ed\'e5"\par
    responsible_organs: [ADMINISTRATUM]\par
    suggested_task_id: TASK-20260512-AGENTS-MD\par
\par
  - id: TH-004\par
    title: "4 \'e8\'e7 10 \'ee\'f0\'e3\'e0\'ed\'ee\'e2 \'ef\'ee\'eb\'ed\'ee\'f1\'f2\'fc\'fe \'ee\'f2\'f1\'f3\'f2\'f1\'f2\'e2\'f3\'fe\'f2"\par
    severity: BLOCKER\par
    area: architecture\par
    evidence_paths:\par
      - ORGANS/\par
      - DOCS/TASK_LIFECYCLE_V0_1.md\par
    problem: "Custodes, Strategium, Schola Imperialis, Throne \'ed\'e5 \'f1\'f3\'f9\'e5\'f1\'f2\'e2\'f3\'fe\'f2"\par
    operational_impact: "Task lifecycle \'ed\'e5 \'ec\'ee\'e6\'e5\'f2 \'e8\'f1\'ef\'ee\'eb\'ed\'ff\'f2\'fc\'f1\'ff end-to-end"\par
    recommended_fix: "\'d1\'ee\'e7\'e4\'e0\'f2\'fc \'ec\'e8\'ed\'e8\'ec\'e0\'eb\'fc\'ed\'fb\'e5 scaffold \'e4\'eb\'ff \'ea\'e0\'e6\'e4\'ee\'e3\'ee"\par
    acceptance_gate: "ls ORGANS/\{CUSTODES,STRATEGIUM,SCHOLA_IMPERIALIS,THRONE\}/ORGAN_STATUS.json \f1\emdash  \f2\'e2\'f1\'e5 \'f1\'f3\'f9\'e5\'f1\'f2\'e2\'f3\'fe\'f2"\par
    responsible_organs: [DOCTRINARIUM]\par
    suggested_task_id: TASK-20260513-MISSING-ORGANS-SCAFFOLD\par
\par
  - id: TH-005\par
    title: "11 \'e2\'e5\'f0\'f1\'e8\'e9 Sanctum \'e2 \'f2\'f0\'e5\'ea\'e8\'ed\'e3\'e5"\par
    severity: HIGH\par
    area: code_hygiene\par
    evidence_paths:\par
      -\f0\lang9\par
}
 