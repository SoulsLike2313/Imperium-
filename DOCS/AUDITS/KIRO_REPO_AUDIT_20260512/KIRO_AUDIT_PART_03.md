{\rtf1\ansi\deff0\nouicompat{\fonttbl{\f0\fnil\fcharset0 Calibri;}{\f1\fnil Calibri;}{\f2\fnil\fcharset204 Calibri;}{\f3\fnil\fcharset1 Cambria Math;}}
{\*\generator Riched20 10.0.19041}{\*\mmathPr\mmathFont3\mwrapIndent1440 }\viewkind4\uc1 
\pard\sa200\sl276\slmult1\f0\fs22\lang9 # IMPERIUM \f1\emdash  \f2\lang1049\'cf\'ce\'cb\'cd\'db\'c9 \'d2\'c5\'d5\'cd\'c8\'d7\'c5\'d1\'ca\'c8\'c9 \'c0\'d3\'c4\'c8\'d2 (\'d4\'c8\'cd\'c0\'cb\'dc\'cd\'c0\'df \'d7\'c0\'d1\'d2\'dc)\par
## \'d1\'e5\'ea\'f6\'e8\'e8 10\f1\endash 12 (\f2\'e7\'e0\'e2\'e5\'f0\'f8\'e5\'ed\'e8\'e5) | \'c0\'f3\'e4\'e8\'f2\'ee\'f0: Kiro | 2026-05-12\par
\par
---\par
\par
# 10. FINDINGS.YAML (\'ef\'f0\'ee\'e4\'ee\'eb\'e6\'e5\'ed\'e8\'e5)\par
\par
```yaml\par
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
    problem: "Custodes, Strategium, Schola Imperialis, Throne \'ed\'e5 \'f1\'f3\'f9\'e5\'f1\'f2\'e2\'f3\'fe\'f2 \'ea\'e0\'ea \'ef\'e0\'ef\'ea\'e8"\par
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
      - SANCTUM/sanctum_v0_1.py\par
      - SANCTUM/sanctum_v0_2.py\par
      - SANCTUM/sanctum_v0_21.py\par
      - SANCTUM/sanctum_v0_22.py\par
      - SANCTUM/sanctum_v0_23.py\par
      - SANCTUM/sanctum_v0_24.py\par
      - SANCTUM/sanctum_v0_25.py\par
      - SANCTUM/sanctum_v0_26.py\par
      - SANCTUM/sanctum_v0_27.py\par
      - SANCTUM/sanctum_v0_28.py\par
      - SANCTUM/sanctum_v0_29_qt.py\par
    problem: "\'cd\'e5\'f2 \'ec\'e0\'f0\'ea\'e5\'f0\'e0 \'f2\'e5\'ea\'f3\'f9\'e5\'e9 \'e2\'e5\'f0\'f1\'e8\'e8. ~8000 \'f1\'f2\'f0\'ee\'ea \'ec\'b8\'f0\'f2\'e2\'ee\'e3\'ee \'ea\'ee\'e4\'e0. \'cb\'ee\'e6\'ed\'fb\'e5 \'f1\'f0\'e0\'e1\'e0\'f2\'fb\'e2\'e0\'ed\'e8\'ff \'ef\'f0\'e8 \'ef\'ee\'e8\'f1\'ea\'e5."\par
    operational_impact: "\'c0\'e3\'e5\'ed\'f2 \'ec\'ee\'e6\'e5\'f2 \'f1\'eb\'f3\'f7\'e0\'e9\'ed\'ee \'ec\'ee\'e4\'e8\'f4\'e8\'f6\'e8\'f0\'ee\'e2\'e0\'f2\'fc \'f1\'f2\'e0\'f0\'f3\'fe \'e2\'e5\'f0\'f1\'e8\'fe"\par
    recommended_fix: "\'cf\'e5\'f0\'e5\'ec\'e5\'f1\'f2\'e8\'f2\'fc v0.1-v0.28 \'e2 SANCTUM/ARCHIVE/. \'ce\'f1\'f2\'e0\'e2\'e8\'f2\'fc \'f2\'ee\'eb\'fc\'ea\'ee v0.29 + service."\par
    acceptance_gate: "git ls-files 'SANCTUM/sanctum_v0_[0-2][0-8]*.py' | wc -l = 0"\par
    responsible_organs: [MECHANICUS]\par
    suggested_task_id: TASK-20260513-SANCTUM-ARCHIVE-LEGACY\par
\par
  - id: TH-006\par
    title: "\'d5\'e0\'f0\'e4\'ea\'ee\'e4 \'e0\'e1\'f1\'ee\'eb\'fe\'f2\'ed\'ee\'e3\'ee \'ef\'f3\'f2\'e8 E:\\\\IMPERIUM"\par
    severity: HIGH\par
    area: portability\par
    evidence_paths:\par
      - SANCTUM/sanctum_v0_29_qt.py\par
    problem: "IMPERIUM_ROOT = Path(r'E:\\\\IMPERIUM') \'ed\'e0 \'f1\'f2\'f0\'ee\'ea\'e5 46"\par
    operational_impact: "Sanctum \'ed\'e5 \'e7\'e0\'ef\'f3\'f1\'f2\'e8\'f2\'f1\'ff \'ed\'e0 VM2, \'e4\'f0\'f3\'e3\'ee\'ec PC, \'e8\'eb\'e8 \'e2 CI"\par
    recommended_fix: "\'c8\'f1\'ef\'ee\'eb\'fc\'e7\'ee\'e2\'e0\'f2\'fc detect_repo_root() \'e8\'e7 imperium.config"\par
    acceptance_gate: "rg 'E:\\\\\\\\\\\\\\\\IMPERIUM' SANCTUM/sanctum_v0_29_qt.py = 0 \'f0\'e5\'e7\'f3\'eb\'fc\'f2\'e0\'f2\'ee\'e2"\par
    responsible_organs: [MECHANICUS]\par
    suggested_task_id: TASK-20260513-SANCTUM-PORTABLE-ROOT\par
\par
  - id: TH-007\par
    title: "ORGAN_REGISTRY \'f1\'ee\'e4\'e5\'f0\'e6\'e8\'f2 \'f2\'ee\'eb\'fc\'ea\'ee 3 \'e8\'e7 6 \'f1\'f3\'f9\'e5\'f1\'f2\'e2\'f3\'fe\'f9\'e8\'f5 \'ee\'f0\'e3\'e0\'ed\'ee\'e2"\par
    severity: HIGH\par
    area: registry_drift\par
    evidence_paths:\par
      - REGISTRY/ORGAN_REGISTRY.json\par
      - ORGANS/INQUISITION/\par
      - ORGANS/MECHANICUS/\par
      - ORGANS/OFFICIO_AGENTIS/\par
    problem: "Inquisition, Mechanicus, Officio Agentis \'ee\'f2\'f1\'f3\'f2\'f1\'f2\'e2\'f3\'fe\'f2 \'e2 \'f0\'e5\'e5\'f1\'f2\'f0\'e5"\par
    operational_impact: "\'c0\'e3\'e5\'ed\'f2, \'f7\'e8\'f2\'e0\'fe\'f9\'e8\'e9 \'f0\'e5\'e5\'f1\'f2\'f0, \'ed\'e5 \'f3\'e7\'ed\'e0\'e5\'f2 \'ee 3 \'ee\'f0\'e3\'e0\'ed\'e0\'f5"\par
    recommended_fix: "\'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc \'e2\'f1\'e5 6 \'ee\'f0\'e3\'e0\'ed\'ee\'e2. \'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc gate registry_drift_check."\par
    acceptance_gate: "jq '.organs | length' REGISTRY/ORGAN_REGISTRY.json >= 6"\par
    responsible_organs: [ADMINISTRATUM]\par
    suggested_task_id: TASK-20260512-REGISTRY-SYNC\par
\par
  - id: TH-008\par
    title: "\'cd\'e5\'f2 CI/CD pipeline"\par
    severity: HIGH\par
    area: automation\par
    evidence_paths:\par
      - "(\'ee\'f2\'f1\'f3\'f2\'f1\'f2\'e2\'e8\'e5 .github/workflows/)"\par
    problem: "Verification spine \'e7\'e0\'ef\'f3\'f1\'ea\'e0\'e5\'f2\'f1\'ff \'f2\'ee\'eb\'fc\'ea\'ee \'e2\'f0\'f3\'f7\'ed\'f3\'fe"\par
    operational_impact: "\'d0\'e5\'e3\'f0\'e5\'f1\'f1\'e8\'e8 \'ed\'e5 \'eb\'ee\'e2\'ff\'f2\'f1\'ff \'e0\'e2\'f2\'ee\'ec\'e0\'f2\'e8\'f7\'e5\'f1\'ea\'e8 \'ef\'f0\'e8 push"\par
    recommended_fix: "\'d1\'ee\'e7\'e4\'e0\'f2\'fc .github/workflows/verify.yml"\par
    acceptance_gate: "Push \'e2 master \'f2\'f0\'e8\'e3\'e3\'e5\'f0\'e8\'f2 CI \'e8 CI \'ef\'f0\'ee\'f5\'ee\'e4\'e8\'f2"\par
    responsible_organs: [MECHANICUS]\par
    suggested_task_id: TASK-20260514-CI-PIPELINE\par
\par
  - id: TH-009\par
    title: "Continuity packs \'e2 Git-\'f2\'f0\'e5\'ea\'e8\'ed\'e3\'e5"\par
    severity: HIGH\par
    area: repo_hygiene\par
    evidence_paths:\par
      - ORGANS/ADMINISTRATUM/CONTINUITY/PACKS/\par
    problem: "200+ \'f4\'e0\'e9\'eb\'ee\'e2 runtime snapshots \'e2 Git. \'ce\'f1\'ed\'ee\'e2\'ed\'ee\'e9 \'e8\'f1\'f2\'ee\'f7\'ed\'e8\'ea 121K warnings."\par
    operational_impact: "\'d0\'e0\'e7\'e4\'f3\'e2\'e0\'e5\'f2 clone, \'e7\'e0\'e3\'f0\'ff\'e7\'ed\'ff\'e5\'f2 \'ef\'ee\'e8\'f1\'ea, \'e3\'e5\'ed\'e5\'f0\'e8\'f0\'f3\'e5\'f2 \'f8\'f3\'ec"\par
    recommended_fix: "git rm --cached + \'e4\'ee\'e1\'e0\'e2\'e8\'f2\'fc \'e2 .gitignore"\par
    acceptance_gate: "git ls-files 'ORGANS/ADMINISTRATUM/CONTINUITY/PACKS/' | wc -l = 0"\par
    responsible_organs: [ADMINISTRATUM]\par
    suggested_task_id: TASK-20260512-CONTINUITY-PACKS-UNTRACK\par
\par
  - id: TH-010\par
    title: "SCRIPT_REGISTRY \'ef\'ee\'ea\'f0\'fb\'e2\'e0\'e5\'f2 8 \'e8\'e7 50+ \'f1\'ea\'f0\'e8\'ef\'f2\'ee\'e2"\par
    severity: HIGH\par
    area: discoverability\par
    evidence_paths:\par
      - REGISTRY/SCRIPT_REGISTRY.json\par
      - TOOLS/\par
      - ORGANS/*/SCRIPTS/\par
    problem: "Placeholder UNKNOWN entry. \'c1\'ee\'eb\'fc\'f8\'e8\'ed\'f1\'f2\'e2\'ee \'f1\'ea\'f0\'e8\'ef\'f2\'ee\'e2 \'ed\'e5 \'e8\'ed\'e4\'e5\'ea\'f1\'e8\'f0\'ee\'e2\'e0\'ed\'fb."\par
    operational_impact: "\'c0\'e3\'e5\'ed\'f2 \'ed\'e5 \'ec\'ee\'e6\'e5\'f2 \'ee\'e1\'ed\'e0\'f0\'f3\'e6\'e8\'f2\'fc \'e4\'ee\'f1\'f2\'f3\'ef\'ed\'fb\'e5 \'f1\'ea\'f0\'e8\'ef\'f2\'fb \'f7\'e5\'f0\'e5\'e7 \'f0\'e5\'e5\'f1\'f2\'f0"\par
    recommended_fix: "\'c0\'e2\'f2\'ee\'e3\'e5\'ed\'e5\'f0\'e0\'f6\'e8\'ff \'e8\'e7 git ls-files. \'d3\'e4\'e0\'eb\'e8\'f2\'fc UNKNOWN placeholder."\par
    acceptance_gate: "\'ca\'e0\'e6\'e4\'fb\'e9 .py/.ps1 \'e2 TOOLS/ \'e8 ORGANS/*/SCRIPTS/ \'e8\'ec\'e5\'e5\'f2 \'e7\'e0\'ef\'e8\'f1\'fc"\par
    responsible_organs: [MECHANICUS]\par
    suggested_task_id: TASK-20260514-SCRIPT-REGISTRY-COMPLETE\par
\par
  - id: TH-011\par
    title: "GitCliCheckService \'ee\'e1\'f5\'ee\'e4\'e8\'f2 command gateway"\par
    severity: MEDIUM\par
    area: security\par
    evidence_paths:\par
      - SANCTUM/sanctum_git_cli_check_service_v0_1.py\par
    problem: "\'cf\'f0\'ff\'ec\'ee\'e9 subprocess.run \'e4\'eb\'ff PowerShell \'e1\'e5\'e7 allowlist \'ef\'f0\'ee\'e2\'e5\'f0\'ea\'e8"\par
    operational_impact: "\'c5\'f9\'b8 \'ee\'e4\'ed\'e0 \'f2\'ee\'f7\'ea\'e0 \'ee\'e1\'f5\'ee\'e4\'e0 gateway"\par
    recommended_fix: "\'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc command_id \'e2 allowlist. \'cf\'e5\'f0\'e5\'ef\'e8\'f1\'e0\'f2\'fc \'ed\'e0 gateway."\par
    acceptance_gate: "rg 'subprocess' SANCTUM/sanctum_git_cli_check_service_v0_1.py = 0"\par
    responsible_organs: [MECHANICUS]\par
    suggested_task_id: TASK-20260513-SANCTUM-GATEWAY-MIGRATION\par
\par
  - id: TH-012\par
    title: "\'cd\'e5\'f2 type checking / linting"\par
    severity: MEDIUM\par
    area: code_quality\par
    evidence_paths:\par
      - pyproject.toml\par
    problem: "\'cd\'e5\'f2 mypy/ruff \'ea\'ee\'ed\'f4\'e8\'e3\'f3\'f0\'e0\'f6\'e8\'e8. py_compile \'eb\'ee\'e2\'e8\'f2 \'f2\'ee\'eb\'fc\'ea\'ee \'f1\'e8\'ed\'f2\'e0\'ea\'f1\'e8\'f1."\par
    operational_impact: "\'cb\'ee\'e3\'e8\'f7\'e5\'f1\'ea\'e8\'e5 \'ee\'f8\'e8\'e1\'ea\'e8 \'f2\'e8\'ef\'ee\'e2 \'ed\'e5 \'eb\'ee\'e2\'ff\'f2\'f1\'ff"\par
    recommended_fix: "\'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc ruff \'e2 pyproject.toml. \'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc gate."\par
    acceptance_gate: "ruff check src/ scripts/ = 0 errors"\par
    responsible_organs: [MECHANICUS]\par
    suggested_task_id: TASK-20260514-LINTING\par
\par
  - id: TH-013\par
    title: "START_HERE.md \'f3\'f1\'f2\'e0\'f0\'e5\'eb"\par
    severity: MEDIUM\par
    area: navigation\par
    evidence_paths:\par
      - START_HERE.md\par
    problem: "\'d3\'ea\'e0\'e7\'fb\'e2\'e0\'e5\'f2 TASK-20260510, HEAD = TASK-20260512"\par
    operational_impact: "\'c0\'e3\'e5\'ed\'f2 \'ef\'ee\'eb\'f3\'f7\'e0\'e5\'f2 \'f3\'f1\'f2\'e0\'f0\'e5\'e2\'f8\'f3\'fe \'e8\'ed\'f4\'ee\'f0\'ec\'e0\'f6\'e8\'fe"\par
    recommended_fix: "\'c0\'e2\'f2\'ee\'ee\'e1\'ed\'ee\'e2\'eb\'e5\'ed\'e8\'e5 \'ef\'f0\'e8 \'ea\'ee\'ec\'ec\'e8\'f2\'e5 \'e8\'eb\'e8 \'e4\'e8\'ed\'e0\'ec\'e8\'f7\'e5\'f1\'ea\'e8\'e9 \'f3\'ea\'e0\'e7\'e0\'f2\'e5\'eb\'fc"\par
    acceptance_gate: "START_HERE.md Current Task \'f1\'ee\'e2\'ef\'e0\'e4\'e0\'e5\'f2 \'f1 git log -1"\par
    responsible_organs: [ADMINISTRATUM]\par
    suggested_task_id: TASK-20260512-START-HERE-SYNC\par
\par
  - id: TH-014\par
    title: "pyproject.toml \'ed\'e5 \'e4\'e5\'ea\'eb\'e0\'f0\'e8\'f0\'f3\'e5\'f2 PySide6"\par
    severity: MEDIUM\par
    area: dependencies\par
    evidence_paths:\par
      - pyproject.toml\par
    problem: "dependencies = []. Sanctum \'f2\'f0\'e5\'e1\'f3\'e5\'f2 PySide6."\par
    operational_impact: "pip install -e . \'ed\'e5 \'f3\'f1\'f2\'e0\'ed\'ee\'e2\'e8\'f2 GUI \'e7\'e0\'e2\'e8\'f1\'e8\'ec\'ee\'f1\'f2\'e8"\par
    recommended_fix: "\'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc [project.optional-dependencies] gui = ['PySide6>=6.5']"\par
    acceptance_gate: "pip install -e '.[gui]' \'f3\'f1\'f2\'e0\'ed\'e0\'e2\'eb\'e8\'e2\'e0\'e5\'f2 PySide6"\par
    responsible_organs: [MECHANICUS]\par
    suggested_task_id: TASK-20260514-DEPS-DECLARATION\par
\par
  - id: TH-015\par
    title: "\'cc\'ed\'ee\'e6\'e5\'f1\'f2\'e2\'e5\'ed\'ed\'fb\'e5 \'e2\'e5\'f0\'f1\'e8\'e8 Doctrinarium web dashboards"\par
    severity: MEDIUM\par
    area: code_hygiene\par
    evidence_paths:\par
      - ORGANS/DOCTRINARIUM/UTILITY/WEB_DASHBOARD/\par
      - ORGANS/DOCTRINARIUM/UTILITY/WEB_DASHBOARD_V0_6/\par
      - ORGANS/DOCTRINARIUM/UTILITY/WEB_DASHBOARD_V0_6_FIXED/\par
      - ORGANS/DOCTRINARIUM/UTILITY/WEB_DASHBOARD_V0_7/\par
      - ORGANS/DOCTRINARIUM/UTILITY/WEB_DASHBOARD_V0_8/\par
      - ORGANS/DOCTRINARIUM/UTILITY/WEB_DASHBOARD_SOFT/\par
    problem: "6 \'e2\'e5\'f0\'f1\'e8\'e9 web dashboard, \'ed\'e5\'ef\'ee\'ed\'ff\'f2\'ed\'ee \'ea\'e0\'ea\'e0\'ff \'f2\'e5\'ea\'f3\'f9\'e0\'ff"\par
    operational_impact: "\'c0\'e3\'e5\'ed\'f2 \'ed\'e5 \'e7\'ed\'e0\'e5\'f2 \'ea\'e0\'ea\'f3\'fe \'e2\'e5\'f0\'f1\'e8\'fe \'e8\'f1\'ef\'ee\'eb\'fc\'e7\'ee\'e2\'e0\'f2\'fc"\par
    recommended_fix: "\'ce\'f1\'f2\'e0\'e2\'e8\'f2\'fc \'f2\'ee\'eb\'fc\'ea\'ee V0_8. \'ce\'f1\'f2\'e0\'eb\'fc\'ed\'fb\'e5 \'e2 ARCHIVE."\par
    acceptance_gate: "\'d2\'ee\'eb\'fc\'ea\'ee \'ee\'e4\'ed\'e0 WEB_DASHBOARD \'ef\'e0\'ef\'ea\'e0 \'e2 UTILITY"\par
    responsible_organs: [DOCTRINARIUM]\par
    suggested_task_id: TASK-20260514-DOCTRINARIUM-DASHBOARD-CLEANUP\par
\par
  - id: TH-016\par
    title: "\'cc\'ed\'ee\'e6\'e5\'f1\'f2\'e2\'e5\'ed\'ed\'fb\'e5 \'e2\'e5\'f0\'f1\'e8\'e8 Astronomicon dashboard ps1"\par
    severity: LOW\par
    area: code_hygiene\par
    evidence_paths:\par
      - ORGANS/ASTRONOMICON/UTILITY/\par
    problem: "7 \'e2\'e5\'f0\'f1\'e8\'e9 astronomicon_dashboard_v0_*.ps1 + 7 run_* wrappers"\par
    operational_impact: "14 \'f4\'e0\'e9\'eb\'ee\'e2 \'e2\'ec\'e5\'f1\'f2\'ee 2"\par
    recommended_fix: "\'ce\'f1\'f2\'e0\'e2\'e8\'f2\'fc \'f2\'ee\'eb\'fc\'ea\'ee latest. \'ce\'f1\'f2\'e0\'eb\'fc\'ed\'fb\'e5 \'e2 ARCHIVE."\par
    acceptance_gate: "ls ORGANS/ASTRONOMICON/UTILITY/*.ps1 | wc -l <= 2"\par
    responsible_organs: [ASTRONOMICON]\par
    suggested_task_id: TASK-20260515-ASTRA-DASHBOARD-CLEANUP\par
11. RECOMMENDED_TASKS.YAML\par
recommended_tasks:\par
  - task_id: TASK-20260512-WARNING-FLOOD-FIX\par
    title: "\'d3\'e1\'f0\'e0\'f2\'fc continuity packs \'e8\'e7 Git \'e8 \'f1\'ee\'e7\'e4\'e0\'f2\'fc warning baseline"\par
    priority: P0\par
    goal: "\'d1\'ed\'e8\'e7\'e8\'f2\'fc warnings \'f1 121K \'e4\'ee <100. \'d1\'e4\'e5\'eb\'e0\'f2\'fc PASS_WITH_WARNINGS \'ee\'f1\'ec\'fb\'f1\'eb\'e5\'ed\'ed\'fb\'ec."\par
    responsible_organs: [ADMINISTRATUM, INQUISITION]\par
    suggested_executor: Owner + PC agent\par
    files_to_touch:\par
      - .gitignore\par
      - REGISTRY/WARNING_BASELINE.json (\'ed\'ee\'e2\'fb\'e9)\par
      - "git rm --cached ORGANS/ADMINISTRATUM/CONTINUITY/PACKS/"\par
    validation: "python scripts/verify_repo.py \f3\u8594?\f0  warnings < 100"\par
    depends_on: []\par
    risk: MEDIUM (\f2\lang1049\'e8\'e7\'ec\'e5\'ed\'e5\'ed\'e8\'e5 Git history \'e4\'eb\'ff tracked files)\par
\par
  - task_id: TASK-20260512-AGENTS-MD\par
    title: "\'d1\'ee\'e7\'e4\'e0\'f2\'fc AGENTS.md \f1\emdash  \f2\'ec\'e0\'f8\'e8\'ed\'ee\'f7\'e8\'f2\'e0\'e5\'ec\'f3\'fe \'f2\'ee\'f7\'ea\'f3 \'e2\'f5\'ee\'e4\'e0"\par
    priority: P0\par
    goal: "\'cb\'fe\'e1\'ee\'e9 \'e0\'e3\'e5\'ed\'f2 \'e7\'e0 30 \'f1\'e5\'ea\'f3\'ed\'e4 \'ef\'ee\'ed\'e8\'ec\'e0\'e5\'f2: \'f7\'f2\'ee \'e1\'e5\'e7\'ee\'ef\'e0\'f1\'ed\'ee, \'f7\'f2\'ee \'e0\'ea\'f2\'e8\'e2\'ed\'ee, \'ea\'e0\'ea \'e2\'e5\'f0\'e8\'f4\'e8\'f6\'e8\'f0\'ee\'e2\'e0\'f2\'fc."\par
    responsible_organs: [ADMINISTRATUM]\par
    suggested_executor: PC agent\par
    files_to_touch:\par
      - AGENTS.md (\'ed\'ee\'e2\'fb\'e9)\par
    validation: "\'d4\'e0\'e9\'eb \'f1\'f3\'f9\'e5\'f1\'f2\'e2\'f3\'e5\'f2 \'e8 \'f1\'ee\'e4\'e5\'f0\'e6\'e8\'f2 \'f1\'e5\'ea\'f6\'e8\'e8 SAFE_COMMANDS, ACTIVE_SOURCE, LEGACY_ZONES, VERIFY_COMMAND"\par
    depends_on: []\par
    risk: LOW\par
\par
  - task_id: TASK-20260512-REGISTRY-SYNC\par
    title: "\'d1\'e8\'ed\'f5\'f0\'ee\'ed\'e8\'e7\'e8\'f0\'ee\'e2\'e0\'f2\'fc ORGAN_REGISTRY \'f1 \'f0\'e5\'e0\'eb\'fc\'ed\'ee\'f1\'f2\'fc\'fe"\par
    priority: P0\par
    goal: "\'d0\'e5\'e5\'f1\'f2\'f0 \'ee\'f2\'f0\'e0\'e6\'e0\'e5\'f2 \'e2\'f1\'e5 \'f1\'f3\'f9\'e5\'f1\'f2\'e2\'f3\'fe\'f9\'e8\'e5 \'ee\'f0\'e3\'e0\'ed\'fb."\par
    responsible_organs: [ADMINISTRATUM]\par
    suggested_executor: PC agent\par
    files_to_touch:\par
      - REGISTRY/ORGAN_REGISTRY.json\par
    validation: "jq '.organs | length' REGISTRY/ORGAN_REGISTRY.json >= 6"\par
    depends_on: []\par
    risk: LOW\par
\par
  - task_id: TASK-20260512-START-HERE-SYNC\par
    title: "\'ce\'e1\'ed\'ee\'e2\'e8\'f2\'fc START_HERE.md \'e4\'ee \'f2\'e5\'ea\'f3\'f9\'e5\'e3\'ee \'f1\'ee\'f1\'f2\'ee\'ff\'ed\'e8\'ff"\par
    priority: P1\par
    goal: "START_HERE \'ee\'f2\'f0\'e0\'e6\'e0\'e5\'f2 HEAD \'ea\'ee\'ec\'ec\'e8\'f2."\par
    responsible_organs: [ADMINISTRATUM]\par
    suggested_executor: PC agent\par
    files_to_touch:\par
      - START_HERE.md\par
    validation: "Current Task \'e2 START_HERE.md \'f1\'ee\'e2\'ef\'e0\'e4\'e0\'e5\'f2 \'f1 git log -1 --oneline"\par
    depends_on: []\par
    risk: LOW\par
\par
  - task_id: TASK-20260513-SANCTUM-GATEWAY-MIGRATION\par
    title: "\'cf\'e5\'f0\'e5\'ef\'e8\'f1\'e0\'f2\'fc Sanctum subprocess \'e2\'fb\'e7\'ee\'e2\'fb \'ed\'e0 command gateway"\par
    priority: P0\par
    goal: "\'c2\'f1\'e5 \'ea\'ee\'ec\'e0\'ed\'e4\'fb \'e2 Sanctum \'e8\'e4\'f3\'f2 \'f7\'e5\'f0\'e5\'e7 allowlist. \'cf\'ee\'eb\'ed\'fb\'e9 audit trail."\par
    responsible_organs: [MECHANICUS, INQUISITION]\par
    suggested_executor: PC agent\par
    files_to_touch:\par
      - SANCTUM/sanctum_v0_29_qt.py\par
      - SANCTUM/sanctum_git_cli_check_service_v0_1.py\par
      - REGISTRY/COMMAND_ALLOWLIST.json\par
    validation: "rg 'subprocess\\\\.(run|Popen)' SANCTUM/ \f3\u8594?\f0  \f2\lang1049\'f2\'ee\'eb\'fc\'ea\'ee \'e2 \'ea\'ee\'ec\'ec\'e5\'ed\'f2\'e0\'f0\'e8\'ff\'f5 \'e8\'eb\'e8 0"\par
    depends_on: []\par
    risk: MEDIUM (\'ec\'ee\'e6\'e5\'f2 \'f1\'eb\'ee\'ec\'e0\'f2\'fc transfer \'e5\'f1\'eb\'e8 allowlist \'ed\'e5\'ef\'ee\'eb\'ed\'fb\'e9)\par
\par
  - task_id: TASK-20260513-SANCTUM-PORTABLE-ROOT\par
    title: "\'d3\'e1\'f0\'e0\'f2\'fc \'f5\'e0\'f0\'e4\'ea\'ee\'e4 E:\\\\IMPERIUM \'e8\'e7 Sanctum"\par
    priority: P1\par
    goal: "Sanctum \'e7\'e0\'ef\'f3\'f1\'ea\'e0\'e5\'f2\'f1\'ff \'ed\'e0 \'eb\'fe\'e1\'ee\'e9 \'ec\'e0\'f8\'e8\'ed\'e5."\par
    responsible_organs: [MECHANICUS]\par
    suggested_executor: PC agent\par
    files_to_touch:\par
      - SANCTUM/sanctum_v0_29_qt.py\par
    validation: "rg 'E:\\\\\\\\\\\\\\\\IMPERIUM' SANCTUM/sanctum_v0_29_qt.py = 0"\par
    depends_on: []\par
    risk: LOW\par
\par
  - task_id: TASK-20260513-SANCTUM-ARCHIVE-LEGACY\par
    title: "\'c0\'f0\'f5\'e8\'e2\'e8\'f0\'ee\'e2\'e0\'f2\'fc Sanctum v0.1\f1\endash v0.28"\par
    priority: P1\par
    goal: "\f2\'d3\'e1\'f0\'e0\'f2\'fc \'ec\'b8\'f0\'f2\'e2\'fb\'e9 \'ea\'ee\'e4 \'e8\'e7 \'e0\'ea\'f2\'e8\'e2\'ed\'ee\'e9 \'e7\'ee\'ed\'fb."\par
    responsible_organs: [MECHANICUS]\par
    suggested_executor: PC agent\par
    files_to_touch:\par
      - SANCTUM/sanctum_v0_1.py \f3\u8594?\f0  SANCTUM/ARCHIVE/\par
      - "... \f2\lang1049\'f7\'e5\'f0\'e5\'e7 sanctum_v0_28.py"\par
      - SANCTUM/CURRENT_VERSION.json (\'ed\'ee\'e2\'fb\'e9)\par
    validation: "git ls-files 'SANCTUM/sanctum_v0_[0-2][0-8]*.py' | wc -l = 0"\par
    depends_on: []\par
    risk: LOW\par
\par
  - task_id: TASK-20260513-MISSING-ORGANS-SCAFFOLD\par
    title: "\'d1\'ee\'e7\'e4\'e0\'f2\'fc scaffold \'e4\'eb\'ff Custodes, Strategium, Schola Imperialis, Throne"\par
    priority: P1\par
    goal: "\'c2\'f1\'e5 10 \'ee\'f0\'e3\'e0\'ed\'ee\'e2 \'f1\'f3\'f9\'e5\'f1\'f2\'e2\'f3\'fe\'f2 \'f5\'ee\'f2\'ff \'e1\'fb \'ea\'e0\'ea scaffold."\par
    responsible_organs: [DOCTRINARIUM]\par
    suggested_executor: PC agent\par
    files_to_touch:\par
      - ORGANS/CUSTODES/ORGAN_STATUS.json\par
      - ORGANS/CUSTODES/README.md\par
      - ORGANS/STRATEGIUM/ORGAN_STATUS.json\par
      - ORGANS/STRATEGIUM/README.md\par
      - ORGANS/SCHOLA_IMPERIALIS/ORGAN_STATUS.json\par
      - ORGANS/SCHOLA_IMPERIALIS/README.md\par
      - ORGANS/THRONE/ORGAN_STATUS.json\par
      - ORGANS/THRONE/README.md\par
    validation: "ls ORGANS/*/ORGAN_STATUS.json | wc -l = 10"\par
    depends_on: []\par
    risk: LOW\par
\par
  - task_id: TASK-20260514-CI-PIPELINE\par
    title: "\'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc GitHub Actions CI"\par
    priority: P1\par
    goal: "\'c0\'e2\'f2\'ee\'ec\'e0\'f2\'e8\'f7\'e5\'f1\'ea\'e0\'ff \'e2\'e5\'f0\'e8\'f4\'e8\'ea\'e0\'f6\'e8\'ff \'ef\'f0\'e8 \'ea\'e0\'e6\'e4\'ee\'ec push."\par
    responsible_organs: [MECHANICUS]\par
    suggested_executor: PC agent\par
    files_to_touch:\par
      - .github/workflows/verify.yml (\'ed\'ee\'e2\'fb\'e9)\par
    validation: "Push \'e2 master \'f2\'f0\'e8\'e3\'e3\'e5\'f0\'e8\'f2 workflow, workflow \'ef\'f0\'ee\'f5\'ee\'e4\'e8\'f2"\par
    depends_on: [TASK-20260512-WARNING-FLOOD-FIX]\par
    risk: LOW\par
\par
  - task_id: TASK-20260514-SCRIPT-REGISTRY-COMPLETE\par
    title: "\'cf\'ee\'eb\'ed\'e0\'ff \'e0\'e2\'f2\'ee\'e3\'e5\'ed\'e5\'f0\'e0\'f6\'e8\'ff SCRIPT_REGISTRY"\par
    priority: P2\par
    goal: "\'c2\'f1\'e5 \'f1\'ea\'f0\'e8\'ef\'f2\'fb \'e8\'ed\'e4\'e5\'ea\'f1\'e8\'f0\'ee\'e2\'e0\'ed\'fb \'e8 discoverable."\par
    responsible_organs: [MECHANICUS]\par
    suggested_executor: PC agent\par
    files_to_touch:\par
      - REGISTRY/SCRIPT_REGISTRY.json\par
      - scripts/generate_script_registry.py (\'ed\'ee\'e2\'fb\'e9)\par
    validation: "\'ca\'ee\'eb\'e8\'f7\'e5\'f1\'f2\'e2\'ee \'e7\'e0\'ef\'e8\'f1\'e5\'e9 >= \'ea\'ee\'eb\'e8\'f7\'e5\'f1\'f2\'e2\'ee .py/.ps1 \'e2 TOOLS/ + ORGANS/*/SCRIPTS/ + scripts/"\par
    depends_on: []\par
    risk: LOW\par
\par
  - task_id: TASK-20260514-SANCTUM-MODULARIZE\par
    title: "\'d0\'e0\'e7\'e1\'e8\'f2\'fc Sanctum \'ed\'e0 \'ec\'ee\'e4\'f3\'eb\'e8"\par
    priority: P2\par
    goal: "sanctum_v0_29_qt.py < 200 \'f1\'f2\'f0\'ee\'ea. \'cb\'ee\'e3\'e8\'ea\'e0 \'e2 \'ee\'f2\'e4\'e5\'eb\'fc\'ed\'fb\'f5 \'f4\'e0\'e9\'eb\'e0\'f5."\par
    responsible_organs: [MECHANICUS]\par
    suggested_executor: PC agent\par
    files_to_touch:\par
      - SANCTUM/sanctum_v0_29_qt.py (\'f0\'e5\'f4\'e0\'ea\'f2\'ee\'f0\'e8\'ed\'e3)\par
      - SANCTUM/widgets/ (\'ed\'ee\'e2\'e0\'ff \'ef\'e0\'ef\'ea\'e0)\par
      - SANCTUM/services/ (\'ed\'ee\'e2\'e0\'ff \'ef\'e0\'ef\'ea\'e0)\par
    validation: "wc -l SANCTUM/sanctum_v0_29_qt.py < 200"\par
    depends_on: [TASK-20260513-SANCTUM-GATEWAY-MIGRATION]\par
    risk: MEDIUM\par
\par
  - task_id: TASK-20260514-LINTING\par
    title: "\'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc ruff linting"\par
    priority: P2\par
    goal: "\'d1\'f2\'e0\'f2\'e8\'f7\'e5\'f1\'ea\'e0\'ff \'ef\'f0\'ee\'e2\'e5\'f0\'ea\'e0 \'ea\'e0\'f7\'e5\'f1\'f2\'e2\'e0 \'ea\'ee\'e4\'e0."\par
    responsible_organs: [MECHANICUS]\par
    suggested_executor: PC agent\par
    files_to_touch:\par
      - pyproject.toml\par
    validation: "ruff check src/ scripts/ tests/ = 0 errors"\par
    depends_on: []\par
    risk: LOW\par
\par
  - task_id: TASK-20260514-DEPS-DECLARATION\par
    title: "\'c4\'e5\'ea\'eb\'e0\'f0\'e8\'f0\'ee\'e2\'e0\'f2\'fc PySide6 \'e2 pyproject.toml"\par
    priority: P2\par
    goal: "\'d7\'e8\'f1\'f2\'e0\'ff \'f3\'f1\'f2\'e0\'ed\'ee\'e2\'ea\'e0 \'e7\'e0\'e2\'e8\'f1\'e8\'ec\'ee\'f1\'f2\'e5\'e9."\par
    responsible_organs: [MECHANICUS]\par
    suggested_executor: PC agent\par
    files_to_touch:\par
      - pyproject.toml\par
    validation: "pip install -e '.[gui]' \'f3\'f1\'f2\'e0\'ed\'e0\'e2\'eb\'e8\'e2\'e0\'e5\'f2 PySide6"\par
    depends_on: []\par
    risk: LOW\par
\par
  - task_id: TASK-20260515-VERIFICATION-PANEL-SANCTUM\par
    title: "\'c4\'ee\'e1\'e0\'e2\'e8\'f2\'fc Verification Gates \'ef\'e0\'ed\'e5\'eb\'fc \'e2 Sanctum"\par
    priority: P2\par
    goal: "Sanctum \'ef\'ee\'ea\'e0\'e7\'fb\'e2\'e0\'e5\'f2 \'f0\'e5\'e0\'eb\'fc\'ed\'fb\'e5 gate results."\par
    responsible_organs: [MECHANICUS]\par
    suggested_executor: PC agent\par
    files_to_touch:\par
      - SANCTUM/widgets/verification_panel.py (\'ed\'ee\'e2\'fb\'e9)\par
      - SANCTUM/sanctum_v0_29_qt.py\par
    validation: "Sanctum \'ee\'f2\'ee\'e1\'f0\'e0\'e6\'e0\'e5\'f2 5 gates \'f1 verdict \'f6\'e2\'e5\'f2\'e0\'ec\'e8"\par
    depends_on: [TASK-20260514-SANCTUM-MODULARIZE]\par
    risk: LOW\par
\par
  - task_id: TASK-20260515-ARSENAL-V0-1\par
    title: "Arsenal v0.1 \f1\emdash  \f2\'ea\'e0\'f2\'e0\'eb\'ee\'e3 \'e8\'ed\'f1\'f2\'f0\'f3\'ec\'e5\'ed\'f2\'ee\'e2"\par
    priority: P3\par
    goal: "\'c0\'e3\'e5\'ed\'f2\'fb \'ec\'ee\'e3\'f3\'f2 \'ee\'e1\'ed\'e0\'f0\'f3\'e6\'e8\'e2\'e0\'f2\'fc \'e8 \'e2\'fb\'e7\'fb\'e2\'e0\'f2\'fc tools \'f7\'e5\'f0\'e5\'e7 \'e5\'e4\'e8\'ed\'fb\'e9 \'ea\'e0\'f2\'e0\'eb\'ee\'e3."\par
    responsible_organs: [MECHANICUS]\par
    suggested_executor: PC agent\par
    files_to_touch:\par
      - ARSENAL/ (\'ed\'ee\'e2\'e0\'ff \'ef\'e0\'ef\'ea\'e0)\par
      - ARSENAL/ARSENAL_REGISTRY.json\par
      - ARSENAL/tools/verify_repo/TOOL_MANIFEST.json\par
      - ARSENAL/tools/git_cli_check/TOOL_MANIFEST.json\par
    validation: "ARSENAL_REGISTRY.json \'f1\'ee\'e4\'e5\'f0\'e6\'e8\'f2 >= 3 tools"\par
    depends_on: [TASK-20260513-SANCTUM-GATEWAY-MIGRATION]\par
    risk: LOW\par
\par
  - task_id: TASK-20260520-TASK-ORCHESTRATOR-MVP\par
    title: "Task Orchestrator MVP"\par
    priority: P3\par
    goal: "\'cc\'e8\'ed\'e8\'ec\'e0\'eb\'fc\'ed\'fb\'e9 \'e8\'f1\'ef\'ee\'eb\'ed\'ff\'e5\'ec\'fb\'e9 pipeline: register \f3\u8594?\f0  preflight \f3\u8594?\f0  stage_map \f3\u8594?\f0  execute \f3\u8594?\f0  receipt"\par
    responsible_organs: [ADMINISTRATUM, ASTRONOMICON, DOCTRINARIUM]\par
    suggested_executor: PC agent + VM2\par
    files_to_touch:\par
      - src/imperium/orchestrator/ (\f2\lang1049\'ed\'ee\'e2\'e0\'ff \'ef\'e0\'ef\'ea\'e0)\par
      - src/imperium/orchestrator/pipeline.py\par
      - src/imperium/orchestrator/stage_machine.py\par
      - tests/test_orchestrator.py\par
    validation: "python -m pytest tests/test_orchestrator.py \'ef\'f0\'ee\'f5\'ee\'e4\'e8\'f2"\par
    depends_on: [TASK-20260513-MISSING-ORGANS-SCAFFOLD, TASK-20260513-SANCTUM-GATEWAY-MIGRATION]\par
    risk: HIGH (core architecture decision)\par
12. \'c8\'d2\'ce\'c3\'ce\'c2\'c0\'df \'d1\'c2\'ce\'c4\'ca\'c0\par
\'d1\'f2\'e0\'f2\'f3\'f1 \'f0\'e5\'ef\'ee\'e7\'e8\'f2\'ee\'f0\'e8\'ff\par
WORKBENCH \f1\emdash  \f2\'f0\'e0\'e1\'ee\'f7\'e8\'e9 \'f1\'f2\'e5\'ed\'e4 \'e8\'ed\'e6\'e5\'ed\'e5\'f0\'e0. \'cd\'e5 operator tool, \'ed\'e5 product.\par
\par
\'d2\'ee\'ef-5 \'ed\'e0\'f5\'ee\'e4\'ee\'ea\par
BLOCKER: Sanctum \'ee\'e1\'f5\'ee\'e4\'e8\'f2 \'f1\'ee\'e1\'f1\'f2\'e2\'e5\'ed\'ed\'fb\'e9 command gateway \'f7\'e5\'f0\'e5\'e7 raw subprocess \f1\emdash  security boundary \f2\'ed\'e0\'f0\'f3\'f8\'e5\'ed\'e0 \'e8\'e7\'ed\'f3\'f2\'f0\'e8\par
BLOCKER: 121 449 warnings \'ef\'f0\'e5\'e2\'f0\'e0\'f9\'e0\'fe\'f2 verification spine \'e2 \'e1\'e5\'f1\'ef\'ee\'eb\'e5\'e7\'ed\'fb\'e9 \'f8\'f3\'ec \f1\emdash  \f2\'ed\'e5\'f2 baseline, \'ed\'e5\'f2 regression detection\par
BLOCKER: \'cd\'e5\'f2 AGENTS.md \f1\emdash  \f2\'ea\'e0\'e6\'e4\'fb\'e9 \'ed\'ee\'e2\'fb\'e9 \'e0\'e3\'e5\'ed\'f2 \'f1\'eb\'e5\'ef \'ef\'f0\'e8 \'e2\'f5\'ee\'e4\'e5 \'e2 \'f0\'e5\'ef\'ee\'e7\'e8\'f2\'ee\'f0\'e8\'e9\par
BLOCKER: 4 \'e8\'e7 10 \'ee\'f0\'e3\'e0\'ed\'ee\'e2 \'ed\'e5 \'f1\'f3\'f9\'e5\'f1\'f2\'e2\'f3\'fe\'f2 \f1\emdash  task lifecycle \f2\'ed\'e5\'e8\'f1\'ef\'ee\'eb\'ed\'e8\'ec\par
HIGH: 11 \'e2\'e5\'f0\'f1\'e8\'e9 Sanctum + 6 \'e2\'e5\'f0\'f1\'e8\'e9 Doctrinarium dashboard + 7 \'e2\'e5\'f0\'f1\'e8\'e9 Astronomicon dashboard = ~30 \'ec\'b8\'f0\'f2\'e2\'fb\'f5 \'f4\'e0\'e9\'eb\'ee\'e2 \'e7\'e0\'e3\'f0\'ff\'e7\'ed\'ff\'fe\'f2 \'ef\'ee\'e8\'f1\'ea\par
\'d2\'ee\'ef-5 \'f1\'eb\'e5\'e4\'f3\'fe\'f9\'e8\'f5 \'e7\'e0\'e4\'e0\'f7\par
TASK-20260512-WARNING-FLOOD-FIX \f1\emdash  \f2\'f3\'e1\'f0\'e0\'f2\'fc continuity packs \'e8\'e7 Git, \'f1\'ee\'e7\'e4\'e0\'f2\'fc baseline (P0, Owner + PC)\par
TASK-20260512-AGENTS-MD \f1\emdash  \f2\'f1\'ee\'e7\'e4\'e0\'f2\'fc \'ec\'e0\'f8\'e8\'ed\'ee\'f7\'e8\'f2\'e0\'e5\'ec\'f3\'fe \'f2\'ee\'f7\'ea\'f3 \'e2\'f5\'ee\'e4\'e0 (P0, PC agent, 15 \'ec\'e8\'ed\'f3\'f2)\par
TASK-20260513-SANCTUM-GATEWAY-MIGRATION \f1\emdash  \f2\'ef\'e5\'f0\'e5\'ef\'e8\'f1\'e0\'f2\'fc subprocess \'ed\'e0 gateway (P0, PC agent, 2 \'f7\'e0\'f1\'e0)\par
TASK-20260512-REGISTRY-SYNC \f1\emdash  \f2\'f1\'e8\'ed\'f5\'f0\'ee\'ed\'e8\'e7\'e8\'f0\'ee\'e2\'e0\'f2\'fc ORGAN_REGISTRY (P0, PC agent, 10 \'ec\'e8\'ed\'f3\'f2)\par
TASK-20260513-MISSING-ORGANS-SCAFFOLD \f1\emdash  \f2\'f1\'ee\'e7\'e4\'e0\'f2\'fc scaffold \'e4\'eb\'ff 4 \'ee\'f0\'e3\'e0\'ed\'ee\'e2 (P1, PC agent, 30 \'ec\'e8\'ed\'f3\'f2)\par
\'ca\'eb\'fe\'f7\'e5\'e2\'fb\'e5 \'ec\'e5\'f2\'f0\'e8\'ea\'e8\par
\'cc\'e5\'f2\'f0\'e8\'ea\'e0\tab\'c7\'ed\'e0\'f7\'e5\'ed\'e8\'e5\par
Tracked files\tab 6929\par
Active source files (estimate)\tab ~200\par
Signal/noise ratio\tab ~3%\par
Verification verdict\tab PASS_WITH_WARNINGS\par
Warnings\tab 121 449\par
Blockers\tab 0\par
Tests\tab 6/6 pass\par
Organs present\tab 6/10\par
Organs in registry\tab 3/10\par
Scripts in registry\tab 8/50+\par
Sanctum versions tracked\tab 11\par
Command gateway bypasses\tab 3 locations\par
CI/CD\tab None\par
\'d4\'e8\'ed\'e0\'eb\'fc\'ed\'ee\'e5 \'f1\'eb\'ee\'e2\'ee\par
\'d4\'f3\'ed\'e4\'e0\'ec\'e5\'ed\'f2 \'f1\'e8\'eb\'fc\'ed\'fb\'e9. Command gateway, receipt model, verification gates, path policy \f1\emdash  \f2\'fd\'f2\'ee \'ef\'f0\'e0\'e2\'e8\'eb\'fc\'ed\'e0\'ff \'e0\'f0\'f5\'e8\'f2\'e5\'ea\'f2\'f3\'f0\'e0. \'cf\'f0\'ee\'e1\'eb\'e5\'ec\'e0 \'ed\'e5 \'e2 \'e4\'e8\'e7\'e0\'e9\'ed\'e5, \'e0 \'e2 \'ed\'e0\'ea\'ee\'ef\'eb\'e5\'ed\'ed\'ee\'ec \'e4\'ee\'eb\'e3\'e5: \'f1\'eb\'e8\'f8\'ea\'ee\'ec \'ec\'ed\'ee\'e3\'ee \'e2\'e5\'f0\'f1\'e8\'e9, \'f1\'eb\'e8\'f8\'ea\'ee\'ec \'ec\'ed\'ee\'e3\'ee snapshots \'e2 Git, \'f1\'eb\'e8\'f8\'ea\'ee\'ec \'ec\'e0\'eb\'ee \'e0\'e2\'f2\'ee\'ec\'e0\'f2\'e8\'e7\'e0\'f6\'e8\'e8 \'e4\'eb\'ff \'ef\'ee\'e4\'e4\'e5\'f0\'e6\'e0\'ed\'e8\'ff \'ef\'ee\'f0\'ff\'e4\'ea\'e0.\par
\par
\'cf\'f0\'e8\'ee\'f0\'e8\'f2\'e5\'f2 #1: \'f1\'ed\'e8\'e7\'e8\'f2\'fc \'f8\'f3\'ec. \'d3\'e1\'f0\'e0\'f2\'fc continuity packs, \'e0\'f0\'f5\'e8\'e2\'e8\'f0\'ee\'e2\'e0\'f2\'fc legacy, \'f1\'ee\'e7\'e4\'e0\'f2\'fc AGENTS.md. \'cf\'ee\'f1\'eb\'e5 \'fd\'f2\'ee\'e3\'ee \'ea\'e0\'e6\'e4\'fb\'e9 \'f1\'eb\'e5\'e4\'f3\'fe\'f9\'e8\'e9 \'f8\'e0\'e3 \'e1\'f3\'e4\'e5\'f2 \'e2 3x \'e1\'fb\'f1\'f2\'f0\'e5\'e5, \'ef\'ee\'f2\'ee\'ec\'f3 \'f7\'f2\'ee \'e0\'e3\'e5\'ed\'f2\'fb \'f1\'ec\'ee\'e3\'f3\'f2 \'ee\'f0\'e8\'e5\'ed\'f2\'e8\'f0\'ee\'e2\'e0\'f2\'fc\'f1\'ff.\par
\par
\'cf\'f0\'e8\'ee\'f0\'e8\'f2\'e5\'f2 #2: \'e7\'e0\'ea\'f0\'fb\'f2\'fc security hole. Sanctum \'e4\'ee\'eb\'e6\'e5\'ed \'e8\'f1\'ef\'ee\'eb\'fc\'e7\'ee\'e2\'e0\'f2\'fc \'f1\'e2\'ee\'e9 \'e6\'e5 gateway. \'c8\'ed\'e0\'f7\'e5 \'e2\'f1\'ff \'e0\'f0\'f5\'e8\'f2\'e5\'ea\'f2\'f3\'f0\'e0 \f1\emdash  \f2\'e4\'e5\'ea\'ee\'f0\'e0\'f6\'e8\'ff.\par
\par
\'cf\'f0\'e8\'ee\'f0\'e8\'f2\'e5\'f2 #3: \'e0\'e2\'f2\'ee\'ec\'e0\'f2\'e8\'e7\'e8\'f0\'ee\'e2\'e0\'f2\'fc verification. CI + baseline + regression detection. \'c1\'e5\'e7 \'fd\'f2\'ee\'e3\'ee \'ea\'e0\'e6\'e4\'fb\'e9 push \f1\emdash  \f2\'f0\'f3\'eb\'e5\'f2\'ea\'e0.\par
\par
\'c0\'f3\'e4\'e8\'f2 \'e7\'e0\'e2\'e5\'f0\'f8\'b8\'ed. \'d4\'e0\'e9\'eb\'fb \'ed\'e5 \'f1\'ee\'e7\'e4\'e0\'ed\'fb, \'f0\'e5\'ef\'ee\'e7\'e8\'f2\'ee\'f0\'e8\'e9 \'ed\'e5 \'ec\'ee\'e4\'e8\'f4\'e8\'f6\'e8\'f0\'ee\'e2\'e0\'ed.\f0\lang9\par
}
 