# ADVISORY RESPONSE — Kiro San-Cleaning / Backend Truth / Scriptorium + Arsenal + Mechanicus

- advisory_id: ADVISORY-RESPONSE-20260513-KIRO-SAN-CLEANING-BACKEND-TRUTH-V0_1
- source: Kiro
- status: raw_advisory_not_canon
- task_context: TASK-20260513-SAN-CLEANING-BACKEND-TRUTH-SCRIPTORIUM-ARSENAL-MECHANICUS-V0_1
- created_by: Owner manual paste
- canon_rule: Raw advisory is not canon until reviewed, registered, reconciled, and modernized by IMPERIUM.

---

## Owner Paste Zone


Понял задачу. Это масштабный архитектурный advisory для san-cleaning и backend truth hardening. Начну с исследования текущего состояния репозитория.

Теперь у меня достаточно данных для полного advisory. Начинаю формировать ответ.

---

# SAN-CLEANING / BACKEND TRUTH / SCRIPTORIUM + ARSENAL + MECHANICUS HARDENING ARC

## ADVISORY ARCHITECTURE PACK

**TASK_ID:** TASK-20260513-SAN-CLEANING-BACKEND-TRUTH-SCRIPTORIUM-ARSENAL-MECHANICUS-V0_1  
**HEAD:** efe74dd0abf7d5b11ef305876832db1f827bcdb4  
**DATE:** 2026-05-13  
**MODE:** Hard architecture audit — no fake green

---

## SECTION 1 — EXECUTIVE VERDICT

### 1.1 Hard Diagnosis

**Что вероятно не так с текущим состоянием проекта:**

| Проблема | Доказательство | Влияние |
|----------|----------------|---------|
| **Script registration coverage ~60%** | 54 скрипта в TOOLS+scripts, 35 зарегистрировано в SCRIPT_REGISTRY.json | Незарегистрированные скрипты = неконтролируемое выполнение |
| **Warning flood** | 117,625 warnings в verify_repo.py | Маскирует реальные проблемы, создаёт "warning blindness" |
| **7,084 файлов .py/.ps1/.sh в репо** | Большинство в ARTIFACTS/ARCHIVE/CONTINUITY | Невозможно отличить активные скрипты от legacy |
| **MECHANICUS без ORGAN_CONTRACT.json** | Файл не существует | Орган не operational, не может владеть script reliability |
| **Дублирование регистров** | REGISTRY/SCRIPT_REGISTRY.json + ORGANS/MECHANICUS/SCRIPT_REGISTRY.json | Неясно какой источник правды |
| **Ad hoc PowerShell в чате** | Паттерн из истории проекта | Нет reusability, нет receipts, нет regression protection |

### 1.2 Почему проект замедляется

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ПРИЧИННО-СЛЕДСТВЕННАЯ ЦЕПЬ                       │
├─────────────────────────────────────────────────────────────────────┤
│  Unindexed files → Agent confusion → Wrong file edits              │
│                                                                     │
│  No script registry coverage → Repeated ad hoc commands            │
│                                                                     │
│  Ad hoc commands → No receipts → No learning → Same errors repeat  │
│                                                                     │
│  Warning flood → Can't see new problems → False confidence         │
│                                                                     │
│  No MECHANICUS operational → No script repair loop → Fragile tools │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.3 Почему ad hoc PowerShell блоки опасны как долгосрочный паттерн

| Риск | Описание |
|------|----------|
| **Нет версионирования** | Команда в чате не имеет commit history |
| **Нет receipts** | Результат выполнения теряется после сессии |
| **Нет regression protection** | Та же ошибка повторится в следующей сессии |
| **Нет dry-run** | Опасные команды выполняются без preview |
| **Нет error learning** | Ошибка не записывается в error registry |
| **Context loss** | Новый агент не знает что работало раньше |
| **Copy-paste drift** | Каждая копия команды немного отличается |

### 1.4 Что должно быть исправлено до reliable large task execution

**P0 — Блокеры:**
1. Script registration coverage ≥ 90% для TOOLS/ и scripts/
2. MECHANICUS ORGAN_CONTRACT.json создан
3. Error registry schema определена
4. Launcher pattern для замены ad hoc commands

**P1 — Критические улучшения:**
1. File taxonomy applied to repo
2. Orphan file detection operational
3. Dashboard truth coverage ≥ 80%
4. Warning flood classified (legacy vs new)

---

## SECTION 2 — SAN-CLEANING TAXONOMY

### 2.1 File/Folder Classification System

| Class ID | Purpose | Allowed Location | Tracking | TTL | Owner Organ | Checker | Dashboard | Cleanup Rule |
|----------|---------|------------------|----------|-----|-------------|---------|-----------|--------------|
| `CORE_FOUNDATION` | Essential project structure | Root, src/, schemas/ | Git tracked | Permanent | ADMINISTRATUM | verify_repo.py | ✓ | Never delete |
| `ORGAN_DOCTRINE` | Organ definitions and contracts | ORGANS/*/ORGAN_CONTRACT.json, ORGANS/*/README.md | Git tracked | Permanent | Per organ | organ_contract_check | ✓ | Owner approval |
| `ACTIVE_REGISTERED_SCRIPT` | Operational scripts in registry | TOOLS/, scripts/ | Git tracked | Permanent | MECHANICUS | check_script_registry | ✓ | Deprecation chain |
| `SCRIPT_CANDIDATE` | Scripts not yet registered | TOOLS/, scripts/, ORGANS/*/SCRIPTS/ | Git tracked | 30 days | MECHANICUS | orphan_script_check | ⚠ | Register or quarantine |
| `EXTERNAL_TOOL_CAPABILITY` | Tool/capability references | REGISTRY/ARSENAL_*.json | Git tracked | Permanent | MECHANICUS | check_arsenal_registry | ✓ | Version update |
| `CURRENT_STATE` | Live operational state | CURRENT_STATE/ | Git tracked | Until superseded | ADMINISTRATUM | current_state_freshness | ✓ | Update on arc change |
| `TASK_RECORD` | Task definitions and results | ORGANS/ASTRONOMICON/REGISTRY/TASK_CANDIDATES/ | Git tracked | Permanent | ASTRONOMICON | task_registration_check | ✓ | Archive after completion |
| `STAGE_RECORD` | Stage maps and progress | ORGANS/ASTRONOMICON/REGISTRY/STAGE_MAPS/ | Git tracked | Permanent | ASTRONOMICON | stage_map_check | ✓ | Archive after completion |
| `ADVISORY_INPUT` | External advisory (raw) | ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_INPUTS/ | Git tracked | Until reconciled | ASTRONOMICON | advisory_status_check | ⚠ | Reconcile or reject |
| `GENERATED_REPORT` | Runtime-generated reports | .imperium_runtime/**/REPORT.json | .gitignore | 7 days | MECHANICUS | report_freshness_check | ✓ | Auto-cleanup |
| `RECEIPT` | Execution evidence | .imperium_runtime/**/RECEIPT.json | .gitignore | 30 days | MECHANICUS | receipt_validity_check | ✓ | Archive or delete |
| `BUNDLE` | Transfer packages | INBOX/VM2_BUNDLES/, .imperium_runtime/bundles/ | .gitignore | 14 days | ADMINISTRATUM | bundle_integrity_check | ✓ | Quarantine then delete |
| `TEMPORARY_WORK` | In-progress work files | .imperium_runtime/tmp/, _BUILD/ | .gitignore | 24 hours | MECHANICUS | temp_file_check | ⚠ | Auto-delete |
| `QUARANTINE` | Suspicious/rejected files | INBOX/QUARANTINE/, QUARANTINE/ | .gitignore | 90 days | INQUISITION | quarantine_review | ⚠ | Owner decision |
| `LEGACY_OBSOLETE` | Old versions, deprecated | ARCHIVE/, ORGANS/*/CONTINUITY/PACKS/ | Git tracked | Permanent | ADMINISTRATUM | legacy_inventory | — | Do not delete without approval |
| `SHOULD_NOT_TRACK` | Files that should be ignored | __pycache__/, *.pyc, .pytest_cache/ | .gitignore | 0 | MECHANICUS | no_pycache_tracked | — | Delete immediately |
| `PRIVATE_LOCAL_ONLY` | Secrets, local config | PRIVATE_CONTEXT_LOCAL/, *_LOCAL/ | .gitignore | Permanent | Owner | boundary_scan | — | Never commit |
| `UNKNOWN_ORPHAN` | Unclassified files | Any | Depends | 7 days | INQUISITION | orphan_file_check | ⚠ | Classify or quarantine |

### 2.2 Classification Decision Tree

```
                    ┌─────────────────┐
                    │   File Found    │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │ In .gitignore or _LOCAL?    │
              └──────────────┬──────────────┘
                    YES      │      NO
                     │       │       │
         ┌───────────┘       │       └───────────┐
         ▼                   │                   ▼
  PRIVATE_LOCAL_ONLY         │         ┌────────────────┐
  or GENERATED_REPORT        │         │ In REGISTRY?   │
  or RECEIPT                 │         └───────┬────────┘
  or BUNDLE                  │            YES  │  NO
  or TEMPORARY_WORK          │             │   │   │
                             │    ┌────────┘   │   └────────┐
                             │    ▼            │            ▼
                             │  ACTIVE_        │      ┌──────────┐
                             │  REGISTERED_    │      │ In TOOLS │
                             │  SCRIPT or      │      │ scripts? │
                             │  EXTERNAL_TOOL  │      └────┬─────┘
                             │                 │      YES  │  NO
                             │                 │       │   │   │
                             │                 │  ┌────┘   │   └────┐
                             │                 │  ▼        │        ▼
                             │                 │ SCRIPT_   │   UNKNOWN_
                             │                 │ CANDIDATE │   ORPHAN
                             │                 │           │
                             └─────────────────┴───────────┘
```

---

## SECTION 3 — METRICS FOR TRUTH AND CLEANLINESS

### 3.1 Core Metrics Table

| Metric ID | Name | Formula | Data Source | Acceptable | Warning | Blocker | Dashboard Display |
|-----------|------|---------|-------------|------------|---------|---------|-------------------|
| `M001` | Script Registration Coverage | `registered_scripts / total_scripts_in_TOOLS_scripts * 100` | SCRIPT_REGISTRY.json, file scan | ≥ 90% | 70-89% | < 70% | Percentage bar |
| `M002` | Tool Registration Coverage | `registered_tools / known_tools * 100` | ARSENAL_TOOL_INDEX.json | ≥ 80% | 60-79% | < 60% | Percentage bar |
| `M003` | Orphan File Count | `files_not_in_any_taxonomy_class` | File scan + taxonomy rules | 0 | 1-10 | > 10 | Count badge |
| `M004` | Stale Report Count | `reports_older_than_TTL` | .imperium_runtime scan | 0 | 1-5 | > 5 | Count badge |
| `M005` | Duplicate Bundle Count | `bundles_with_same_sha256` | Bundle scan | 0 | 1-2 | > 2 | Count badge |
| `M006` | Untracked Dirty File Count | `git_status_untracked_count` | git status | 0 | 1-5 | > 5 | Count badge |
| `M007` | Warning Count | `verify_repo_warnings` | verify_repo.py | < 1000 | 1000-10000 | > 10000 | Count + trend |
| `M008` | Blocker Count | `active_blockers_in_registries` | READY_FOR_AGENT, WARNING_BUDGET | 0 | — | > 0 | Count badge (red) |
| `M009` | Broken Checker Count | `checkers_with_exit_code_nonzero` | Checker execution | 0 | 1 | > 1 | Count badge |
| `M010` | Missing Receipt Count | `scripts_without_recent_receipt` | Receipt scan | 0 | 1-3 | > 3 | Count badge |
| `M011` | Undocumented Script Count | `scripts_without_purpose_field` | SCRIPT_REGISTRY.json | 0 | 1-5 | > 5 | Count badge |
| `M012` | Script Reliability Score | `(successful_runs / total_runs) * 100` | Error registry | ≥ 95% | 80-94% | < 80% | Percentage bar |
| `M013` | Dashboard Truth Coverage | `data_sources_with_fresh_data / total_data_sources * 100` | Dashboard data builder | ≥ 80% | 60-79% | < 60% | Percentage bar |
| `M014` | Task-Path Traceability | `tasks_with_complete_stage_chain / total_tasks * 100` | ASTRONOMICON registry | ≥ 90% | 70-89% | < 70% | Percentage bar |
| `M015` | Bundle Route Consistency | `bundles_matching_route_policy / total_bundles * 100` | BUNDLE_ROUTE_REGISTRY | 100% | 90-99% | < 90% | Percentage bar |
| `M016` | Artifact Quarantine Coverage | `suspicious_artifacts_in_quarantine / suspicious_artifacts_total * 100` | Quarantine scan | 100% | 80-99% | < 80% | Percentage bar |
| `M017` | No-Fake-Green Compliance | `verdicts_with_evidence / total_verdicts * 100` | Verdict scan | 100% | — | < 100% | Boolean badge |

### 3.2 Metric Collection Script Interface

```python
# Proposed: TOOLS/collect_backend_health_metrics_v0_1.py
def collect_metrics(repo_root: Path) -> dict:
    return {
        "collected_at_utc": datetime.utcnow().isoformat(),
        "repo_head": get_git_head(repo_root),
        "metrics": {
            "M001_script_registration_coverage": calculate_m001(repo_root),
            "M002_tool_registration_coverage": calculate_m002(repo_root),
            # ... etc
        },
        "verdicts": {
            "overall": "PASS" | "PASS_WITH_WARNINGS" | "BLOCKED",
            "blockers": [...],
            "warnings": [...]
        }
    }
```

---

## SECTION 4 — SCRIPTORIUM DESIGN

### 4.1 SCRIPTORIUM Purpose

SCRIPTORIUM is the **script registry and script truth layer** — not a new organ, but a support layer owned by MECHANICUS.

**Responsibilities:**
- Index every script in repo
- Track script metadata, dependencies, safety classification
- Enable script discovery by agents
- Support script reliability tracking
- Provide deprecation chains

### 4.2 SCRIPTORIUM Registry Entry Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SCRIPTORIUM Registry Entry v0.2",
  "type": "object",
  "required": [
    "script_id",
    "path",
    "name",
    "owner_organ",
    "purpose",
    "platform",
    "runtime",
    "status"
  ],
  "properties": {
    "script_id": {
      "type": "string",
      "pattern": "^SCRIPT-[A-Z0-9-]+$",
      "description": "Unique script identifier"
    },
    "path": {
      "type": "string",
      "description": "Relative path from repo root"
    },
    "name": {
      "type": "string",
      "description": "Filename"
    },
    "owner_organ": {
      "type": "string",
      "enum": ["ADMINISTRATUM", "ASTRONOMICON", "DOCTRINARIUM", "MECHANICUS", "INQUISITION", "OFFICIO_AGENTIS", "CUSTODES", "STRATEGIUM", "SCHOLA_IMPERIALIS", "THRONE", "UNKNOWN"]
    },
    "support_layer": {
      "type": "string",
      "const": "SCRIPTORIUM"
    },
    "purpose": {
      "type": "string",
      "minLength": 10,
      "description": "What this script does"
    },
    "platform": {
      "type": "string",
      "enum": ["CROSS_PLATFORM", "WINDOWS_ONLY", "UBUNTU_ONLY"]
    },
    "runtime": {
      "type": "string",
      "enum": ["PYTHON", "PYTHON3", "POWERSHELL", "BASH", "NODE", "UNKNOWN"]
    },
    "entrypoint_command": {
      "type": "string",
      "description": "Exact command to run this script"
    },
    "required_args": {
      "type": "array",
      "items": {"type": "string"}
    },
    "optional_args": {
      "type": "array",
      "items": {"type": "string"}
    },
    "reads": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Paths/resources this script reads"
    },
    "writes": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Paths/resources this script writes"
    },
    "side_effects": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["SAFE_READONLY", "WRITES_RUNTIME_ONLY", "MODIFIES_REPO", "NETWORK_ACCESS", "OWNER_ONLY"]
      }
    },
    "produces_receipts": {"type": "boolean"},
    "receipt_paths": {
      "type": "array",
      "items": {"type": "string"}
    },
    "modifies_repo": {"type": "boolean"},
    "commit_push_capable": {"type": "boolean"},
    "vm2_sync_capable": {"type": "boolean"},
    "requires_owner_approval": {"type": "boolean"},
    "safe_for_servitor": {"type": "boolean"},
    "dangerous_if_misused": {"type": "boolean"},
    "idempotent": {"type": "boolean"},
    "known_dependencies": {
      "type": "array",
      "items": {"type": "string"}
    },
    "expected_exit_codes": {
      "type": "array",
      "items": {"type": "integer"}
    },
    "example_safe_invocation": {"type": "string"},
    "verification_command": {"type": "string"},
    "task_stage_compatibility": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Which task/stage types this script supports"
    },
    "checker_relation": {
      "type": "string",
      "description": "Related checker script_id if any"
    },
    "known_failures": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "failure_id": {"type": "string"},
          "description": {"type": "string"},
          "fixed": {"type": "boolean"}
        }
      }
    },
    "last_verified_at": {
      "type": ["string", "null"],
      "format": "date-time"
    },
    "last_verified_commit": {
      "type": ["string", "null"]
    },
    "status": {
      "type": "string",
      "enum": ["REGISTERED", "ACTIVE", "CANDIDATE", "DEPRECATED", "QUARANTINE", "BROKEN", "NEEDS_REVIEW", "BLOCKED"]
    },
    "replacement_chain": {
      "type": ["string", "null"],
      "description": "script_id of replacement if deprecated"
    },
    "dashboard_fields": {
      "type": "object",
      "properties": {
        "show_in_dashboard": {"type": "boolean"},
        "category": {"type": "string"},
        "quick_action": {"type": "boolean"}
      }
    }
  }
}
```

### 4.3 Example SCRIPTORIUM Entries

**Checker Script:**
```json
{
  "script_id": "SCRIPT-CHECK-SCRIPT-REGISTRY-V0_1",
  "path": "TOOLS/check_script_registry_v0_1.py",
  "name": "check_script_registry_v0_1.py",
  "owner_organ": "MECHANICUS",
  "support_layer": "SCRIPTORIUM",
  "purpose": "Validate SCRIPT_REGISTRY.json against schema and check script file existence",
  "platform": "CROSS_PLATFORM",
  "runtime": "PYTHON3",
  "entrypoint_command": "python3 TOOLS/check_script_registry_v0_1.py --repo-root . --human",
  "required_args": [],
  "optional_args": ["--repo-root", "--human", "--json-out"],
  "reads": ["REGISTRY/SCRIPT_REGISTRY.json", "schemas/script_registry.schema.json", "TOOLS/", "scripts/"],
  "writes": [".imperium_runtime/scriptorium/check/"],
  "side_effects": ["WRITES_RUNTIME_ONLY"],
  "produces_receipts": true,
  "receipt_paths": [".imperium_runtime/scriptorium/check/SCRIPT_REGISTRY_CHECK_RECEIPT.json"],
  "modifies_repo": false,
  "commit_push_capable": false,
  "vm2_sync_capable": false,
  "requires_owner_approval": false,
  "safe_for_servitor": true,
  "dangerous_if_misused": false,
  "idempotent": true,
  "known_dependencies": ["python3"],
  "expected_exit_codes": [0, 2],
  "example_safe_invocation": "python3 TOOLS/check_script_registry_v0_1.py --repo-root . --human",
  "verification_command": "python3 TOOLS/check_script_registry_v0_1.py --repo-root . --human",
  "task_stage_compatibility": ["PREFLIGHT", "VERIFICATION", "AUDIT"],
  "checker_relation": null,
  "known_failures": [],
  "last_verified_at": null,
  "last_verified_commit": null,
  "status": "REGISTERED",
  "replacement_chain": null,
  "dashboard_fields": {
    "show_in_dashboard": true,
    "category": "SCRIPTORIUM",
    "quick_action": true
  }
}
```

**Bundle Intake Script:**
```json
{
  "script_id": "SCRIPT-BUNDLE-FETCH-REVIEW-V0_1",
  "path": "TOOLS/bundle_fetch_review_v0_1.py",
  "name": "bundle_fetch_review_v0_1.py",
  "owner_organ": "ADMINISTRATUM",
  "support_layer": "SCRIPTORIUM",
  "purpose": "Universal bundle fetch and review launcher — replaces ad hoc scp/review commands",
  "platform": "CROSS_PLATFORM",
  "runtime": "PYTHON3",
  "entrypoint_command": "python3 TOOLS/bundle_fetch_review_v0_1.py --source vm2 --task TASK-XXX --mode review",
  "required_args": ["--source", "--task"],
  "optional_args": ["--mode", "--dry-run", "--json-out"],
  "reads": ["SSH_COMMAND_LIBRARY/", "REGISTRY/BUNDLE_ROUTE_REGISTRY.json"],
  "writes": ["INBOX/VM2_BUNDLES/", ".imperium_runtime/bundle_intake_review/"],
  "side_effects": ["NETWORK_ACCESS", "WRITES_RUNTIME_ONLY"],
  "produces_receipts": true,
  "receipt_paths": [".imperium_runtime/bundle_intake_review/*/BUNDLE_FETCH_RECEIPT.json"],
  "modifies_repo": false,
  "commit_push_capable": false,
  "vm2_sync_capable": true,
  "requires_owner_approval": false,
  "safe_for_servitor": true,
  "dangerous_if_misused": false,
  "idempotent": true,
  "known_dependencies": ["python3", "ssh", "scp"],
  "expected_exit_codes": [0, 2, 3],
  "example_safe_invocation": "python3 TOOLS/bundle_fetch_review_v0_1.py --source vm2 --task TASK-20260513-XXX --mode review --dry-run",
  "verification_command": "python3 TOOLS/bundle_fetch_review_v0_1.py --help",
  "task_stage_compatibility": ["BUNDLE_INTAKE", "REVIEW"],
  "checker_relation": "SCRIPT-CHECK-BUNDLE-ROUTE-REGISTRY-V0_1",
  "known_failures": [],
  "last_verified_at": null,
  "last_verified_commit": null,
  "status": "CANDIDATE",
  "replacement_chain": null,
  "dashboard_fields": {
    "show_in_dashboard": true,
    "category": "BUNDLE_OPS",
    "quick_action": true
  }
}
```

**VM2 Sync Script:**
```json
{
  "script_id": "SCRIPT-VM2-EXACT-SYNC-V0_1",
  "path": "TOOLS/vm2_exact_sync_v0_1.py",
  "name": "vm2_exact_sync_v0_1.py",
  "owner_organ": "ADMINISTRATUM",
  "support_layer": "SCRIPTORIUM",
  "purpose": "Exact sync of VM2 repo to match PC HEAD — replaces ad hoc git fetch/reset commands",
  "platform": "CROSS_PLATFORM",
  "runtime": "PYTHON3",
  "entrypoint_command": "python3 TOOLS/vm2_exact_sync_v0_1.py --target vm2 --mode verify",
  "required_args": ["--target"],
  "optional_args": ["--mode", "--force", "--dry-run"],
  "reads": ["SSH_COMMAND_LIBRARY/", "git state"],
  "writes": [".imperium_runtime/vm2_sync/"],
  "side_effects": ["NETWORK_ACCESS", "WRITES_RUNTIME_ONLY"],
  "produces_receipts": true,
  "receipt_paths": [".imperium_runtime/vm2_sync/VM2_SYNC_RECEIPT.json"],
  "modifies_repo": false,
  "commit_push_capable": false,
  "vm2_sync_capable": true,
  "requires_owner_approval": true,
  "safe_for_servitor": false,
  "dangerous_if_misused": true,
  "idempotent": true,
  "known_dependencies": ["python3", "ssh", "git"],
  "expected_exit_codes": [0, 2],
  "example_safe_invocation": "python3 TOOLS/vm2_exact_sync_v0_1.py --target vm2 --mode verify --dry-run",
  "verification_command": "python3 TOOLS/vm2_exact_sync_v0_1.py --help",
  "task_stage_compatibility": ["VM2_SYNC", "CONTOUR_ALIGNMENT"],
  "checker_relation": null,
  "known_failures": [],
  "last_verified_at": null,
  "last_verified_commit": null,
  "status": "CANDIDATE",
  "replacement_chain": null,
  "dashboard_fields": {
    "show_in_dashboard": true,
    "category": "VM2_OPS",
    "quick_action": false
  }
}
```

---

## SECTION 5 — ARSENAL DESIGN

### 5.1 ARSENAL Purpose

ARSENAL is the **registry of external tools and capabilities** — tracks what's installed, what's available, what's approved.

### 5.2 ARSENAL Registry Entry Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ARSENAL Tool Entry v0.2",
  "type": "object",
  "required": ["tool_id", "name", "category", "platform", "tool_type", "status"],
  "properties": {
    "tool_id": {
      "type": "string",
      "pattern": "^TOOL-[A-Z0-9-]+$"
    },
    "name": {"type": "string"},
    "category": {
      "type": "string",
      "enum": ["RUNTIME", "CLI_SEARCH", "CLI_FORMAT", "CLI_VIEW", "GIT_TOOL", "ARCHIVE", "CONNECTIVITY", "SECURITY", "PYTHON_LIB", "SCHEMA_VALID", "DIAGRAM", "DOCS", "DATABASE", "BROWSER", "GUI_FRAMEWORK", "EDITOR"]
    },
    "platform": {
      "type": "string",
      "enum": ["CROSS_PLATFORM", "WINDOWS_ONLY", "UBUNTU_ONLY"]
    },
    "tool_type": {
      "type": "string",
      "enum": ["runtime", "cli", "library", "app", "service"]
    },
    "purpose_for_imperium": {"type": "string"},
    "owner_use_case": {"type": "string"},
    "servitor_use_case": {"type": "string"},
    "installation_method": {"type": "string"},
    "verification_command": {"type": "string"},
    "version_command": {"type": "string"},
    "license_cost": {
      "type": "string",
      "enum": ["FREE_OPEN_SOURCE", "FREE_PROPRIETARY", "PAID", "UNKNOWN"]
    },
    "offline_capability": {
      "type": "string",
      "enum": ["YES", "YES_AFTER_INSTALL", "PARTIAL", "NO"]
    },
    "privacy_risk": {
      "type": "string",
      "enum": ["LOW", "MEDIUM", "HIGH"]
    },
    "security_risk": {
      "type": "string",
      "enum": ["LOW", "MEDIUM", "HIGH"]
    },
    "resource_cost": {
      "type": "string",
      "enum": ["LOW", "MEDIUM", "HIGH"]
    },
    "install_status": {
      "type": "object",
      "properties": {
        "pc_windows": {"type": "string", "enum": ["INSTALLED", "NOT_INSTALLED", "UNKNOWN"]},
        "vm2_ubuntu": {"type": "string", "enum": ["INSTALLED", "NOT_INSTALLED", "UNKNOWN"]}
      }
    },
    "allowed_use_cases": {
      "type": "array",
      "items": {"type": "string"}
    },
    "forbidden_use_cases": {
      "type": "array",
      "items": {"type": "string"}
    },
    "owner_approval": {
      "type": "string",
      "enum": ["APPROVED", "PENDING", "REJECTED", "NOT_REQUIRED"]
    },
    "official_url": {"type": ["string", "null"]},
    "docs_url": {"type": ["string", "null"]},
    "status": {
      "type": "string",
      "enum": ["AVAILABLE_CONFIRMED", "RECOMMENDED_NOT_APPROVED", "NEEDS_SOURCE_VERIFICATION", "

Продолжаю с того места, где прервался — завершаю ARSENAL schema и далее.

---

### 5.2 ARSENAL Registry Entry Schema (продолжение)

```json
    "status": {
      "type": "string",
      "enum": ["AVAILABLE_CONFIRMED", "RECOMMENDED_NOT_APPROVED", "NEEDS_SOURCE_VERIFICATION", "UNKNOWN", "DEPRECATED", "BLOCKED"]
    },
    "dashboard_fields": {
      "type": "object",
      "properties": {
        "show_in_dashboard": {"type": "boolean"},
        "category_group": {"type": "string"},
        "health_indicator": {"type": "boolean"}
      }
    }
  }
}
```

### 5.3 Example ARSENAL Entries

**Git:**
```json
{
  "tool_id": "TOOL-GIT",
  "name": "Git",
  "category": "GIT_TOOL",
  "platform": "CROSS_PLATFORM",
  "tool_type": "cli",
  "purpose_for_imperium": "Version control, commit, push, fetch, status — core truth source",
  "owner_use_case": "All repo operations",
  "servitor_use_case": "Read-only status/log queries, bundle provenance",
  "installation_method": "apt install git / Git for Windows installer",
  "verification_command": "git --version",
  "version_command": "git --version",
  "license_cost": "FREE_OPEN_SOURCE",
  "offline_capability": "YES",
  "privacy_risk": "LOW",
  "security_risk": "LOW",
  "resource_cost": "LOW",
  "install_status": {
    "pc_windows": "INSTALLED",
    "vm2_ubuntu": "INSTALLED"
  },
  "allowed_use_cases": ["status", "log", "diff", "fetch", "rev-parse", "ls-files"],
  "forbidden_use_cases": ["push from VM2", "force push", "rebase without approval"],
  "owner_approval": "APPROVED",
  "official_url": "https://git-scm.com/",
  "docs_url": "https://git-scm.com/doc",
  "status": "AVAILABLE_CONFIRMED",
  "dashboard_fields": {
    "show_in_dashboard": true,
    "category_group": "CORE",
    "health_indicator": true
  }
}
```

**SSH/SCP:**
```json
{
  "tool_id": "TOOL-OPENSSH",
  "name": "OpenSSH",
  "category": "CONNECTIVITY",
  "platform": "CROSS_PLATFORM",
  "tool_type": "cli",
  "purpose_for_imperium": "Secure PC<->VM2 route operations, bundle transfer",
  "owner_use_case": "SSH-based intake/sync workflows",
  "servitor_use_case": "Route truth command compatibility",
  "installation_method": "Usually preinstalled / apt install openssh-client",
  "verification_command": "ssh -V",
  "version_command": "ssh -V",
  "license_cost": "FREE_OPEN_SOURCE",
  "offline_capability": "YES",
  "privacy_risk": "LOW",
  "security_risk": "MEDIUM",
  "resource_cost": "LOW",
  "install_status": {
    "pc_windows": "INSTALLED",
    "vm2_ubuntu": "INSTALLED"
  },
  "allowed_use_cases": ["bundle fetch", "vm2 sync", "remote command execution"],
  "forbidden_use_cases": ["credential storage in scripts", "password auth"],
  "owner_approval": "APPROVED",
  "official_url": "https://www.openssh.com/",
  "docs_url": "https://www.openssh.com/manual.html",
  "status": "AVAILABLE_CONFIRMED",
  "dashboard_fields": {
    "show_in_dashboard": true,
    "category_group": "CONNECTIVITY",
    "health_indicator": true
  }
}
```

**Python:**
```json
{
  "tool_id": "TOOL-PYTHON3",
  "name": "Python 3",
  "category": "RUNTIME",
  "platform": "CROSS_PLATFORM",
  "tool_type": "runtime",
  "purpose_for_imperium": "Primary scripting runtime for checkers, builders, validators",
  "owner_use_case": "All Python-based tooling",
  "servitor_use_case": "Script execution, data processing",
  "installation_method": "apt install python3 / python.org installer",
  "verification_command": "python3 --version",
  "version_command": "python3 --version",
  "license_cost": "FREE_OPEN_SOURCE",
  "offline_capability": "YES",
  "privacy_risk": "LOW",
  "security_risk": "LOW",
  "resource_cost": "LOW",
  "install_status": {
    "pc_windows": "INSTALLED",
    "vm2_ubuntu": "INSTALLED"
  },
  "allowed_use_cases": ["all IMPERIUM scripts"],
  "forbidden_use_cases": ["network requests without approval", "file deletion without quarantine"],
  "owner_approval": "APPROVED",
  "official_url": "https://www.python.org/",
  "docs_url": "https://docs.python.org/3/",
  "status": "AVAILABLE_CONFIRMED",
  "dashboard_fields": {
    "show_in_dashboard": true,
    "category_group": "CORE",
    "health_indicator": true
  }
}
```

**PySide6:**
```json
{
  "tool_id": "TOOL-PYSIDE6",
  "name": "PySide6",
  "category": "GUI_FRAMEWORK",
  "platform": "CROSS_PLATFORM",
  "tool_type": "library",
  "purpose_for_imperium": "Sanctum Qt-based dashboard runtime",
  "owner_use_case": "Desktop dashboard UI",
  "servitor_use_case": "UI component development in UI_LAB",
  "installation_method": "pip install PySide6",
  "verification_command": "python3 -c \"import PySide6; print(PySide6.__version__)\"",
  "version_command": "python3 -c \"import PySide6; print(PySide6.__version__)\"",
  "license_cost": "FREE_OPEN_SOURCE",
  "offline_capability": "YES_AFTER_INSTALL",
  "privacy_risk": "LOW",
  "security_risk": "LOW",
  "resource_cost": "MEDIUM",
  "install_status": {
    "pc_windows": "INSTALLED",
    "vm2_ubuntu": "UNKNOWN"
  },
  "allowed_use_cases": ["Sanctum dashboard", "UI_LAB prototypes"],
  "forbidden_use_cases": ["direct dangerous command execution from UI"],
  "owner_approval": "APPROVED",
  "official_url": "https://www.qt.io/qt-for-python",
  "docs_url": "https://doc.qt.io/qtforpython/",
  "status": "AVAILABLE_CONFIRMED",
  "dashboard_fields": {
    "show_in_dashboard": true,
    "category_group": "GUI",
    "health_indicator": true
  }
}
```

**PowerShell:**
```json
{
  "tool_id": "TOOL-POWERSHELL",
  "name": "PowerShell",
  "category": "RUNTIME",
  "platform": "WINDOWS_ONLY",
  "tool_type": "runtime",
  "purpose_for_imperium": "Windows-specific automation, bundle intake, git operations",
  "owner_use_case": "PC-side task execution",
  "servitor_use_case": "Windows-only scripts when Python insufficient",
  "installation_method": "Built into Windows / pwsh for cross-platform",
  "verification_command": "powershell -Command \"$PSVersionTable.PSVersion\"",
  "version_command": "powershell -Command \"$PSVersionTable.PSVersion\"",
  "license_cost": "FREE_OPEN_SOURCE",
  "offline_capability": "YES",
  "privacy_risk": "LOW",
  "security_risk": "MEDIUM",
  "resource_cost": "LOW",
  "install_status": {
    "pc_windows": "INSTALLED",
    "vm2_ubuntu": "NOT_INSTALLED"
  },
  "allowed_use_cases": ["bundle intake", "git operations", "file management"],
  "forbidden_use_cases": ["ad hoc commands in chat without registration"],
  "owner_approval": "APPROVED",
  "official_url": "https://github.com/PowerShell/PowerShell",
  "docs_url": "https://docs.microsoft.com/en-us/powershell/",
  "status": "AVAILABLE_CONFIRMED",
  "dashboard_fields": {
    "show_in_dashboard": true,
    "category_group": "CORE",
    "health_indicator": true
  }
}
```

---

## SECTION 6 — MECHANICUS ORGAN DEFINITION

### 6.1 MECHANICUS Mission

**Mission Statement:**
> MECHANICUS is the execution machinery organ — responsible for script reliability, tool integration, error learning, repair loops, and backend bridges. It ensures that IMPERIUM's automation layer is robust, self-healing, and continuously improving.

### 6.2 MECHANICUS Boundaries

| Owns | Does NOT Own |
|------|--------------|
| Script registry (SCRIPTORIUM) | Task planning (ASTRONOMICON) |
| Tool registry (ARSENAL) | Doctrine/policy (DOCTRINARIUM) |
| Script repair policy | Memory/state (ADMINISTRATUM) |
| Error learning loop | Audit/compliance (INQUISITION) |
| Launcher standards | Agent assignment (OFFICIO_AGENTIS) |
| Backend bridges | UI/dashboard design (SANCTUM) |
| Regression tests for scripts | Security policy (CUSTODES) |
| Environment checks | Strategy (STRATEGIUM) |
| Dependency validation | Training (SCHOLA_IMPERIALIS) |

### 6.3 MECHANICUS Relations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MECHANICUS RELATIONS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DOCTRINARIUM ──────► MECHANICUS                                            │
│    "Script standards must follow doctrine"                                  │
│                                                                             │
│  ADMINISTRATUM ◄────► MECHANICUS                                            │
│    "State tracking for script execution, receipts storage"                  │
│                                                                             │
│  ASTRONOMICON ──────► MECHANICUS                                            │
│    "Task stages require script capabilities"                                │
│                                                                             │
│  MECHANICUS ──────► SCRIPTORIUM (support layer)                             │
│    "Owns script registry"                                                   │
│                                                                             │
│  MECHANICUS ──────► ARSENAL (support layer)                                 │
│    "Owns tool registry"                                                     │
│                                                                             │
│  MECHANICUS ──────► SANCTUM                                                 │
│    "Provides backend bridges for dashboard actions"                         │
│                                                                             │
│  INQUISITION ──────► MECHANICUS                                             │
│    "Audits script reliability, error patterns"                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.4 MECHANICUS File Structure

```
ORGANS/MECHANICUS/
├── ORGAN_CONTRACT.json          # [TO CREATE] Formal organ contract
├── ORGAN_STATUS.json            # [EXISTS] Current status
├── SELF_REPORT.json             # [TO CREATE] Self-assessment
├── README.md                    # [EXISTS] Overview
├── SCRIPT_REPAIR_POLICY.md      # [TO CREATE] How to repair broken scripts
├── ERROR_LEARNING_POLICY.md     # [TO CREATE] How errors become improvements
├── FUNDAMENTAL_SCRIPT_STANDARD.md # [TO CREATE] Universal script requirements
├── BACKEND_BRIDGE_POLICY.md     # [TO CREATE] How dashboards connect to scripts
├── LAUNCHER_STANDARD.md         # [TO CREATE] CLI launcher requirements
├── PORTS/
│   └── ...                      # [EXISTS] Port definitions
├── REGISTRY/
│   ├── SCRIPT_REGISTRY.json     # [EXISTS] Local script registry
│   ├── ERROR_REGISTRY.json      # [TO CREATE] Script failure records
│   └── REPAIR_LOG.json          # [TO CREATE] Repair history
├── REPAIR_SCRIPTS/
│   └── ...                      # [EXISTS] Repair utilities
├── SCRIPTS/
│   └── ...                      # [EXISTS] MECHANICUS-owned scripts
├── SCHEMAS/
│   └── ...                      # [EXISTS] Local schemas
├── TESTS/
│   └── ...                      # [EXISTS] Script tests
└── UTILITY/
    └── ...                      # [EXISTS] Utility scripts
```

### 6.5 MECHANICUS ORGAN_CONTRACT.json (Proposed)

```json
{
  "schema_version": "imperium.organ_contract.v0_2",
  "organ_id": "MECHANICUS",
  "organ_name": "Mechanicus",
  "mission": "Execution machinery, script reliability, tool integration, error learning, repair loops, and backend bridges",
  "status": "SCAFFOLD_NEEDS_HARDENING",
  "maturity_level": "0.2",
  "owner": "IMPERIUM_CORE",
  "created_at": "2026-05-09",
  "updated_at": "2026-05-13",
  "responsibilities": [
    "Own and maintain SCRIPTORIUM (script registry)",
    "Own and maintain ARSENAL (tool registry)",
    "Define and enforce script standards",
    "Track and learn from script failures",
    "Provide repair loops for broken scripts",
    "Validate script dependencies and environment",
    "Provide backend bridges for Sanctum actions",
    "Define launcher standards for CLI tools",
    "Run regression tests for critical scripts"
  ],
  "forbidden_actions": [
    "Execute tasks without ASTRONOMICON stage map",
    "Modify doctrine without DOCTRINARIUM approval",
    "Store state outside designated paths",
    "Delete files without quarantine",
    "Bypass INQUISITION audit requirements",
    "Claim script reliability without evidence"
  ],
  "owned_paths": {
    "read_write": [
      "ORGANS/MECHANICUS/",
      "REGISTRY/SCRIPT_REGISTRY.json",
      "REGISTRY/ARSENAL_TOOL_INDEX.json",
      "REGISTRY/ARSENAL_INSTALL_STATUS.json",
      ".imperium_runtime/mechanicus/"
    ],
    "read_only": [
      "TOOLS/",
      "scripts/",
      "schemas/",
      "REGISTRY/"
    ]
  },
  "required_capabilities": [
    "script_registry_check",
    "arsenal_registry_check",
    "error_registry_write",
    "repair_log_write",
    "backend_bridge_invoke"
  ],
  "produces_receipts": true,
  "receipt_schema": "schemas/mechanicus_receipt.schema.json",
  "dashboard_integration": {
    "provides_data_for": ["SCRIPTORIUM_DASHBOARD", "ARSENAL_DASHBOARD", "BACKEND_HEALTH_DASHBOARD"],
    "action_bridges": ["script_run", "tool_check", "error_record"]
  },
  "dependencies": {
    "organs": ["ADMINISTRATUM", "DOCTRINARIUM"],
    "tools": ["TOOL-PYTHON3", "TOOL-GIT"],
    "schemas": ["script_registry.schema.json", "arsenal_tool.schema.json"]
  },
  "no_fake_green_rules": [
    "Script reliability score must be based on actual execution evidence",
    "Tool availability must be verified, not assumed",
    "Error registry must contain real failures, not placeholders"
  ]
}
```

---

## SECTION 7 — ERROR REGISTRY AND SCRIPT LEARNING LOOP

### 7.1 Error Registry Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Script Error Registry Entry v0.1",
  "type": "object",
  "required": ["error_id", "script_id", "occurred_at", "severity", "status"],
  "properties": {
    "error_id": {
      "type": "string",
      "pattern": "^ERR-[0-9]{8}-[0-9]{6}-[A-Z0-9]+$"
    },
    "script_id": {"type": "string"},
    "script_path": {"type": "string"},
    "occurred_at": {"type": "string", "format": "date-time"},
    "severity": {
      "type": "string",
      "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    },
    "error_type": {
      "type": "string",
      "enum": ["SYNTAX", "RUNTIME", "DEPENDENCY", "PERMISSION", "NETWORK", "DATA", "LOGIC", "ENVIRONMENT", "UNKNOWN"]
    },
    "command_used": {"type": "string"},
    "working_directory": {"type": "string"},
    "environment": {
      "type": "object",
      "properties": {
        "platform": {"type": "string"},
        "python_version": {"type": "string"},
        "powershell_version": {"type": "string"},
        "git_version": {"type": "string"},
        "repo_head": {"type": "string"}
      }
    },
    "exit_code": {"type": "integer"},
    "stdout_capture": {"type": "string"},
    "stderr_capture": {"type": "string"},
    "error_message": {"type": "string"},
    "stack_trace": {"type": ["string", "null"]},
    "suspected_cause": {"type": "string"},
    "reproducibility": {
      "type": "string",
      "enum": ["ALWAYS", "INTERMITTENT", "ONCE", "UNKNOWN"]
    },
    "affected_task": {"type": ["string", "null"]},
    "affected_stage": {"type": ["string", "null"]},
    "repair_decision": {
      "type": "object",
      "properties": {
        "action": {"type": "string", "enum": ["FIX_SCRIPT", "FIX_ENVIRONMENT", "FIX_DATA", "WORKAROUND", "WONTFIX", "DUPLICATE"]},
        "assigned_to": {"type": "string"},
        "deadline": {"type": ["string", "null"]},
        "notes": {"type": "string"}
      }
    },
    "regression_test_required": {"type": "boolean"},
    "regression_test_id": {"type": ["string", "null"]},
    "status": {
      "type": "string",
      "enum": ["NEW", "TRIAGED", "IN_PROGRESS", "REPAIRED", "VERIFIED", "WONTFIX", "DUPLICATE", "CLOSED"]
    },
    "resolved_at": {"type": ["string", "null"]},
    "resolved_by": {"type": ["string", "null"]},
    "resolution_commit": {"type": ["string", "null"]},
    "lessons_learned": {"type": ["string", "null"]}
  }
}
```

### 7.2 Example Error Records

**PowerShell Here-String Issue:**
```json
{
  "error_id": "ERR-20260513-143022-PS1HERESTR",
  "script_id": "SCRIPT-REVIEW-WORKER-BUNDLE-INTAKE-PS1-V0_1",
  "script_path": "TOOLS/review_worker_bundle_intake.ps1",
  "occurred_at": "2026-05-13T14:30:22Z",
  "severity": "HIGH",
  "error_type": "SYNTAX",
  "command_used": "powershell -ExecutionPolicy Bypass -File TOOLS/review_worker_bundle_intake.ps1 -Bundle ...",
  "working_directory": "E:\\IMPERIUM",
  "environment": {
    "platform": "WINDOWS",
    "powershell_version": "5.1",
    "repo_head": "efe74dd0abf7d5b11ef305876832db1f827bcdb4"
  },
  "exit_code": 1,
  "stdout_capture": "",
  "stderr_capture": "The string is missing the terminator: '@.",
  "error_message": "Here-string terminator '@' must be at the beginning of a line",
  "stack_trace": null,
  "suspected_cause": "Here-string closing marker has leading whitespace",
  "reproducibility": "ALWAYS",
  "affected_task": "TASK-20260513-BUNDLE-INTAKE-V0_1",
  "affected_stage": null,
  "repair_decision": {
    "action": "FIX_SCRIPT",
    "assigned_to": "MECHANICUS",
    "deadline": "2026-05-13",
    "notes": "Remove leading whitespace before @' terminator"
  },
  "regression_test_required": true,
  "regression_test_id": "TEST-PS1-HERESTRING-SYNTAX",
  "status": "REPAIRED",
  "resolved_at": "2026-05-13T15:00:00Z",
  "resolved_by": "Owner",
  "resolution_commit": "abc123...",
  "lessons_learned": "Always place here-string terminators at column 0 with no leading whitespace"
}
```

**Wrong Allowlist Causing Blocked Apply:**
```json
{
  "error_id": "ERR-20260513-102015-ALLOWLIST",
  "script_id": "SCRIPT-REVIEW-WORKER-BUNDLE-INTAKE-PS1-V0_1",
  "script_path": "TOOLS/review_worker_bundle_intake.ps1",
  "occurred_at": "2026-05-13T10:20:15Z",
  "severity": "MEDIUM",
  "error_type": "LOGIC",
  "command_used": "powershell ... -Apply",
  "working_directory": "E:\\IMPERIUM",
  "environment": {
    "platform": "WINDOWS",
    "repo_head": "efe74dd0abf7d5b11ef305876832db1f827bcdb4"
  },
  "exit_code": 3,
  "stdout_capture": "BLOCKED: File not in allowlist: SANCTUM/new_file.py",
  "stderr_capture": "",
  "error_message": "Apply blocked due to file not in allowlist",
  "stack_trace": null,
  "suspected_cause": "Allowlist pattern too restrictive, doesn't include new SANCTUM files",
  "reproducibility": "ALWAYS",
  "affected_task": "TASK-20260513-SANCTUM-V0_5",
  "affected_stage": "STAGE-003-APPLY",
  "repair_decision": {
    "action": "FIX_DATA",
    "assigned_to": "Owner",
    "deadline": null,
    "notes": "Update COMMAND_ALLOWLIST.json to include SANCTUM/*.py pattern"
  },
  "regression_test_required": false,
  "regression_test_id": null,
  "status": "REPAIRED",
  "resolved_at": "2026-05-13T10:45:00Z",
  "resolved_by": "Owner",
  "resolution_commit": "def456...",
  "lessons_learned": "Allowlist patterns should be reviewed when adding new file categories"
}
```

**Missing changed_files in Bundle:**
```json
{
  "error_id": "ERR-20260513-091530-NOCHANGED",
  "script_id": "SCRIPT-VERIFY-WORKER-BUNDLE-V0_1",
  "script_path": "TOOLS/verify_worker_bundle.py",
  "occurred_at": "2026-05-13T09:15:30Z",
  "severity": "HIGH",
  "error_type": "DATA",
  "command_used": "python3 TOOLS/verify_worker_bundle.py --bundle INBOX/VM2_BUNDLES/bundle_xyz",
  "working_directory": "E:\\IMPERIUM",
  "environment": {
    "platform": "WINDOWS",
    "python_version": "3.11.4",
    "repo_head": "efe74dd0abf7d5b11ef305876832db1f827bcdb4"
  },
  "exit_code": 2,
  "stdout_capture": "",
  "stderr_capture": "ERROR: changed_files/ directory not found in bundle",
  "error_message": "Bundle missing required changed_files/ directory",
  "stack_trace": null,
  "suspected_cause": "VM2 bundle builder did not include changed_files directory",
  "reproducibility": "ALWAYS",
  "affected_task": "TASK-20260513-VM2-BUNDLE",
  "affected_stage": "STAGE-001-VERIFY",
  "repair_decision": {
    "action": "FIX_SCRIPT",
    "assigned_to": "MECHANICUS",
    "deadline": "2026-05-14",
    "notes": "Update VM2 bundle builder to always include changed_files/"
  },
  "regression_test_required": true,
  "regression_test_id": "TEST-BUNDLE-STRUCTURE-COMPLETE",
  "status": "TRIAGED",
  "resolved_at": null,
  "resolved_by": null,
  "resolution_commit": null,
  "lessons_learned": null
}
```

### 7.3 Script Learning Loop

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SCRIPT LEARNING LOOP                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. DETECT ──────► Script fails with nonzero exit code                      │
│                                                                             │
│  2. CAPTURE ─────► record_script_error_v0_1.py captures:                    │
│                    - command, environment, stdout, stderr                   │
│                    - exit code, stack trace if available                    │
│                                                                             │
│  3. CLASSIFY ────► Error type assigned:                                     │
│                    SYNTAX | RUNTIME | DEPENDENCY | PERMISSION | etc.        │
│                                                                             │
│  4. TRIAGE ──────► Severity and repair decision assigned                    │
│                                                                             │
│  5. REPAIR ──────► Script fixed, tested locally                             │
│                                                                             │
│  6. VERIFY ──────► Regression test added and passes                         │
│                                                                             │
│  7. LEARN ───────► lessons_learned field populated                          │
│                    Pattern added to FUNDAMENTAL_SCRIPT_STANDARD.md          │
│                                                                             │
│  8. CLOSE ───────► Error status = VERIFIED, resolution_commit recorded      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## SECTION 8 — BUNDLE / ARTIFACT / QUARANTINE POLICY

### 8.1 Bundle Locations

| Location | Purpose | Tracking | TTL |
|----------|---------|----------|-----|
| `INBOX/VM2_BUNDLES/` | Incoming bundles from VM2 | .gitignore | 14 days |
| `INBOX/VM2_REVIEW/` | Bundles under review | .gitignore | 7 days |
| `INBOX/QUARANTINE/` | Suspicious/rejected bundles | .gitignore | 90 days |
| `.imperium_runtime/bundles/` | Runtime bundle staging | .gitignore | 7 days |
| `.imperium_runtime/bundle_intake_review/` | Review session data | .gitignore | 7 days |
| `BUNDLES_LOCAL/` | Local-only supplement bundles | .gitignore | Permanent |
| `OUTBOX/VM2_PROMPTS/` | Outgoing prompts to VM2 | .gitignore | 7 days |

### 8.2 Bundle Structure Standard

```
bundle_TASK-YYYYMMDD-XXX/
├── MANIFEST.json              # Required: bundle metadata
├── RECEIPT.json               # Required: execution evidence
├── VERDICT.md                 # Required: human-readable verdict
├── changed_files/             # Required: files to apply
│   ├── TOOLS/
│   │   └── new_script.py
│   └── REGISTRY/
│       └── updated_registry.json
├── repo/                      # Optional: full repo snapshot adapter
│   └── ...
├── sha256/                    # Required: file hashes
│   └── CHANGED_FILES_SHA256.txt
└── evidence/                  # Optional: screenshots, logs
    └── ...
```

### 8.3 Bundle Intake Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BUNDLE INTAKE FLOW                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. FETCH ───────► bundle_fetch_review_v0_1.py --source vm2 --task XXX     │
│                    Downloads bundle to INBOX/VM2_BUNDLES/                   │
│                                                                             │
│  2. VERIFY ──────► verify_worker_bundle.py --bundle <path>                  │
│                    Checks: MANIFEST, sha256, structure, scope               │
│                                                                             │
│  3. REVIEW ──────► review_worker_bundle_intake.ps1 -Bundle <path> -NoApply  │
│                    Shows diff, checks allowlist, emits review report        │
│                                                                             │
│  4. DECIDE ──────► Owner reviews report                                     │
│                    APPROVE → proceed to apply                               │
│                    REJECT → move to QUARANTINE                              │
│                                                                             │
│  5. APPLY ───────► review_worker_bundle_intake.ps1 -Bundle <path> -Apply    │
│                    Copies changed_files to repo                             │
│                                                                             │
│  6. COMMIT ──────► bundle_apply_commit_v0_1.py --task XXX --mode commit     │
│                    Stages, commits with proper message                      │
│                                                                             │
│  7. CLEANUP ─────► Move processed bundle to archive or delete               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.4 Quarantine Policy

| Condition | Action | TTL |
|-----------|--------|-----|
| Bundle fails verify | Move to QUARANTINE, log reason | 90 days |
| Bundle has unexpected files | Move to QUARANTINE, log files | 90 days |
| Bundle scope mismatch | Move to QUARANTINE, log scope | 90 days |
| Owner rejects bundle | Move to QUARANTINE, log reason | 90 days |
| Quarantine TTL expired | Owner decision: delete or archive | — |

---

## SECTION 9 — DASHBOARD ARCHITECTURE

### 9.1 Dashboard Design Principles

1. **Truth First** — Dashboard shows reality, not aspirations
2. **No Fake Buttons** — Buttons only work if backend bridge exists
3. **Evidence Required** — Every status has a data source
4. **Stale Detection** — Show data age, warn if stale
5. **Graceful Degradation** — Missing data shows "UNKNOWN",

Продолжаю с Section 9 — Dashboard Architecture.

---

### 9.1 Dashboard Design Principles (продолжение)

5. **Graceful Degradation** — Missing data shows "UNKNOWN", not fake green
6. **Testable** — Every panel can be verified with Playwright later

### 9.2 Required Dashboards

#### 9.2.1 SCRIPTORIUM Dashboard

| Aspect | Specification |
|--------|---------------|
| **Data Sources** | `REGISTRY/SCRIPT_REGISTRY.json`, file scan of `TOOLS/`, `scripts/` |
| **Panels** | Script list, Registration coverage, Unregistered scripts, Broken scripts, Recent errors |
| **Filters** | By organ, By platform, By status, By safety level |
| **Status Indicators** | ✓ REGISTERED, ⚠ CANDIDATE, ✗ BROKEN, ? UNKNOWN |
| **Warnings** | Unregistered scripts > 0, Broken scripts > 0, Coverage < 90% |
| **Blockers** | Coverage < 70%, Critical script broken |
| **Must Never Fake** | Registration count, Script existence, Error count |
| **Active Buttons (Phase 1)** | "Refresh Data", "Run Check" |
| **Disabled Until Bridge** | "Register Script", "Run Script", "Repair Script" |
| **Playwright Test** | Verify script count matches file count, verify status colors |

#### 9.2.2 ARSENAL Dashboard

| Aspect | Specification |
|--------|---------------|
| **Data Sources** | `REGISTRY/ARSENAL_TOOL_INDEX.json`, `REGISTRY/ARSENAL_INSTALL_STATUS.json`, tool verification commands |
| **Panels** | Tool list, Install status by platform, Approval status, Missing tools |
| **Filters** | By category, By platform, By approval status |
| **Status Indicators** | ✓ INSTALLED, ⚠ NOT_INSTALLED, ? UNKNOWN, ✗ BLOCKED |
| **Warnings** | Required tool not installed, Tool version outdated |
| **Blockers** | Core tool (Git, Python) not available |
| **Must Never Fake** | Install status, Version numbers |
| **Active Buttons (Phase 1)** | "Refresh Data", "Verify Tool" |
| **Disabled Until Bridge** | "Install Tool", "Update Tool" |
| **Playwright Test** | Verify tool count, verify install status matches reality |

#### 9.2.3 SANCTUM Truth Dashboard

| Aspect | Specification |
|--------|---------------|
| **Data Sources** | Git state, `CURRENT_STATE/`, Organ statuses, Recent receipts, Warning budget |
| **Panels** | Git truth (HEAD, branch, dirty), Current focus, Organ health, Recent activity, Warnings/Blockers |
| **Filters** | By organ, By time range |
| **Status Indicators** | ✓ CLEAN, ⚠ DIRTY, ✗ BLOCKED, ↻ STALE |
| **Warnings** | Dirty working tree, Stale CURRENT_STATE, Warning count > budget |
| **Blockers** | READY_FOR_AGENT violations, Fake green detected |
| **Must Never Fake** | Git HEAD, Commit count, Warning count, Blocker list |
| **Active Buttons (Phase 1)** | "Refresh", "Run verify_repo.py", "View Warnings" |
| **Disabled Until Bridge** | "Commit", "Push", "Apply Bundle" |
| **Playwright Test** | Verify HEAD matches `git rev-parse HEAD`, verify warning count |

#### 9.2.4 Global Backend Health Dashboard

| Aspect | Specification |
|--------|---------------|
| **Data Sources** | All metrics from Section 3, All checker outputs, All receipts |
| **Panels** | Overall health score, Metric summary table, Trend charts, Recent errors, Action queue |
| **Filters** | By metric category, By severity, By time range |
| **Status Indicators** | 🟢 HEALTHY, 🟡 WARNING, 🔴 BLOCKED |
| **Warnings** | Any metric in warning threshold |
| **Blockers** | Any metric in blocker threshold, Any checker failing |
| **Must Never Fake** | Metric values, Checker verdicts, Error counts |
| **Active Buttons (Phase 1)** | "Refresh All", "Run All Checkers", "Export Report" |
| **Disabled Until Bridge** | "Auto-Repair", "Batch Apply" |
| **Playwright Test** | Verify all metrics have data sources, verify no fake green |

### 9.3 Dashboard Data Builder Pattern

```python
# TOOLS/build_dashboard_data_v0_1.py

def build_dashboard_data(repo_root: Path, dashboard_id: str) -> dict:
    """Build dashboard data with truth guarantees."""
    
    data = {
        "dashboard_id": dashboard_id,
        "generated_at_utc": datetime.utcnow().isoformat(),
        "repo_head": get_git_head(repo_root),
        "data_sources": {},
        "panels": {},
        "warnings": [],
        "blockers": [],
        "stale_indicators": []
    }
    
    # Each data source must be explicitly loaded and timestamped
    for source_id, source_path in DASHBOARD_SOURCES[dashboard_id].items():
        source_data = load_source(repo_root / source_path)
        data["data_sources"][source_id] = {
            "path": str(source_path),
            "loaded_at": datetime.utcnow().isoformat(),
            "exists": source_data is not None,
            "stale": is_stale(source_data),
            "data": source_data
        }
        
        if source_data is None:
            data["warnings"].append(f"Data source missing: {source_path}")
        elif is_stale(source_data):
            data["stale_indicators"].append(source_id)
    
    # Build panels from data sources
    data["panels"] = build_panels(data["data_sources"], dashboard_id)
    
    # Detect blockers
    data["blockers"] = detect_blockers(data)
    
    return data
```

---

## SECTION 10 — REPLACE CHAT COMMANDS WITH REGISTERED LAUNCHERS

### 10.1 Launcher Script Standards

Every launcher script MUST:

| Requirement | Description |
|-------------|-------------|
| **Self-Description** | `--help` shows purpose, args, examples |
| **Dry-Run Mode** | `--dry-run` shows what would happen without doing it |
| **JSON Output** | `--json-out <path>` writes structured output |
| **Human Output** | `--human` shows colored, formatted output |
| **Plain Text Fallback** | Works without colors in CI/pipe mode |
| **Receipt Generation** | Writes receipt to `.imperium_runtime/` |
| **Error Reporting** | Nonzero exit code + structured error info |
| **Idempotent** | Safe to run multiple times |
| **Registered** | Entry in SCRIPT_REGISTRY.json |

### 10.2 Launcher CLI UX Pattern

```
python3 TOOLS/<launcher>.py \
    --task TASK-YYYYMMDD-XXX \
    --mode <review|apply|commit|verify> \
    [--dry-run] \
    [--human] \
    [--json-out <path>] \
    [--repo-root <path>]
```

### 10.3 Example Launchers

#### 10.3.1 Universal Bundle Fetch/Review Launcher

```
# Instead of:
# scp -r user@vm2:/path/to/bundle ./INBOX/VM2_BUNDLES/
# python3 TOOLS/verify_worker_bundle.py --bundle ...
# powershell ... review_worker_bundle_intake.ps1 ...

# Use:
python3 TOOLS/bundle_fetch_review_v0_1.py \
    --source vm2 \
    --task TASK-20260513-XXX \
    --mode review \
    --human
```

**Script Specification:**
```
Purpose: Fetch bundle from VM2 and run review pipeline
Inputs: --source (vm2|local), --task, --mode (fetch|review|full)
Outputs: Bundle in INBOX/VM2_BUNDLES/, review report in .imperium_runtime/
Side Effects: Network access (scp), writes to INBOX/
Safety: Safe (read-only review by default)
Receipt: .imperium_runtime/bundle_intake_review/<timestamp>/FETCH_REVIEW_RECEIPT.json
```

#### 10.3.2 Controlled Apply/Commit Launcher

```
# Instead of:
# powershell ... -Apply
# git add ...
# git commit -m "..."

# Use:
python3 TOOLS/bundle_apply_commit_v0_1.py \
    --task TASK-20260513-XXX \
    --bundle INBOX/VM2_BUNDLES/bundle_xxx \
    --mode apply \
    --dry-run
```

**Script Specification:**
```
Purpose: Apply reviewed bundle and optionally commit
Inputs: --task, --bundle, --mode (apply|commit|apply-commit)
Outputs: Files copied to repo, commit created
Side Effects: Modifies repo, creates commit
Safety: Requires --dry-run first, Owner approval for commit
Receipt: .imperium_runtime/bundle_apply/APPLY_COMMIT_RECEIPT.json
```

#### 10.3.3 VM2 Exact Sync Launcher

```
# Instead of:
# ssh user@vm2 "cd /path && git fetch origin && git reset --hard origin/master"

# Use:
python3 TOOLS/vm2_exact_sync_v0_1.py \
    --target vm2 \
    --mode verify \
    --human
```

**Script Specification:**
```
Purpose: Sync VM2 repo to match PC HEAD exactly
Inputs: --target (vm2), --mode (verify|sync|force-sync)
Outputs: VM2 repo state report
Side Effects: Network access, VM2 git operations
Safety: verify mode is safe, sync requires approval
Receipt: .imperium_runtime/vm2_sync/VM2_SYNC_RECEIPT.json
```

#### 10.3.4 Script Inventory Builder

```
python3 TOOLS/build_script_inventory_v0_1.py \
    --repo-root . \
    --human \
    --json-out .imperium_runtime/scriptorium/SCRIPT_INVENTORY.json
```

**Script Specification:**
```
Purpose: Scan repo for all scripts and compare with registry
Inputs: --repo-root
Outputs: Inventory report showing registered vs unregistered
Side Effects: None (read-only)
Safety: Safe
Receipt: .imperium_runtime/scriptorium/SCRIPT_INVENTORY_RECEIPT.json
```

#### 10.3.5 Arsenal Inventory Builder

```
python3 TOOLS/build_arsenal_inventory_v0_1.py \
    --repo-root . \
    --verify-install \
    --human
```

**Script Specification:**
```
Purpose: Verify tool availability and compare with registry
Inputs: --repo-root, --verify-install (run verification commands)
Outputs: Tool availability report
Side Effects: Runs verification commands (safe)
Safety: Safe
Receipt: .imperium_runtime/arsenal/ARSENAL_INVENTORY_RECEIPT.json
```

#### 10.3.6 Dashboard Data Builder

```
python3 TOOLS/build_backend_health_dashboard_data_v0_1.py \
    --repo-root . \
    --dashboard backend-health \
    --human \
    --json-out SANCTUM/DASHBOARD/DATA/backend_health.json
```

**Script Specification:**
```
Purpose: Build dashboard data from all sources
Inputs: --repo-root, --dashboard (scriptorium|arsenal|sanctum|backend-health)
Outputs: Dashboard data JSON
Side Effects: None (read-only)
Safety: Safe
Receipt: .imperium_runtime/dashboard/DASHBOARD_BUILD_RECEIPT.json
```

---

## SECTION 11 — REPOSITORY CLEANUP PLAN

### 11.1 Phased Cleanup Approach

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLEANUP PHASES                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase A: SNAPSHOT ──► Capture current truth baseline                       │
│  Phase B: INVENTORY ─► Build file/script/tool inventories                   │
│  Phase C: DETECT ────► Find orphans, duplicates, stale files                │
│  Phase D: CLASSIFY ──► Apply taxonomy to all files                          │
│  Phase E: REGISTER ──► Register all scripts in SCRIPTORIUM                  │
│  Phase F: TOOLS ─────► Register all tools in ARSENAL                        │
│  Phase G: DASHBOARD ─► Build truth dashboards                               │
│  Phase H: QUARANTINE ► Move trash to quarantine (no delete)                 │
│  Phase I: IGNORE ────► Update .gitignore for temp outputs                   │
│  Phase J: REGRESSION ► Add regression checks                                │
│  Phase K: FREEZE ────► Commit cleaned baseline                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 11.2 Phase Details

#### Phase A: Snapshot Current Truth

| Aspect | Specification |
|--------|---------------|
| **Inputs** | Current repo state |
| **Scripts** | `inventory_repo_truth_v0_1.py` |
| **Files Created** | `.imperium_runtime/cleanup/PHASE_A_SNAPSHOT.json` |
| **Checks** | Git status clean, HEAD recorded, file count recorded |
| **Pass Criteria** | Snapshot created with all metrics |
| **Risks** | None (read-only) |
| **Rollback** | N/A |

#### Phase B: Build Inventory Collector

| Aspect | Specification |
|--------|---------------|
| **Inputs** | Phase A snapshot |
| **Scripts** | `build_scriptorium_registry_v0_1.py`, `build_arsenal_registry_v0_1.py` |
| **Files Created** | Expanded `REGISTRY/SCRIPT_REGISTRY.json`, `REGISTRY/ARSENAL_TOOL_INDEX.json` |
| **Checks** | All scripts in TOOLS/ and scripts/ inventoried |
| **Pass Criteria** | Inventory complete, no scan errors |
| **Risks** | Registry format changes |
| **Rollback** | Restore previous registry versions |

#### Phase C: Detect Unknown/Orphan Files

| Aspect | Specification |
|--------|---------------|
| **Inputs** | Phase B inventories, taxonomy rules |
| **Scripts** | `detect_orphan_files_v0_1.py` |
| **Files Created** | `.imperium_runtime/cleanup/ORPHAN_FILE_REPORT.json` |
| **Checks** | Every file classified or marked orphan |
| **Pass Criteria** | Orphan list generated, no false positives on known files |
| **Risks** | False positives (legitimate files marked orphan) |
| **Rollback** | N/A (report only) |

#### Phase D: Classify Files by Taxonomy

| Aspect | Specification |
|--------|---------------|
| **Inputs** | Phase C orphan report, taxonomy rules |
| **Scripts** | `classify_repo_files_v0_1.py` |
| **Files Created** | `.imperium_runtime/cleanup/FILE_CLASSIFICATION.json` |
| **Checks** | Every file has taxonomy class |
| **Pass Criteria** | 100% classification coverage |
| **Risks** | Misclassification |
| **Rollback** | N/A (report only) |

#### Phase E: Register Scripts

| Aspect | Specification |
|--------|---------------|
| **Inputs** | Phase D classification, existing registry |
| **Scripts** | `register_scripts_batch_v0_1.py` |
| **Files Created** | Updated `REGISTRY/SCRIPT_REGISTRY.json` |
| **Checks** | All TOOLS/ and scripts/ files registered |
| **Pass Criteria** | Registration coverage ≥ 90% |
| **Risks** | Incorrect metadata |
| **Rollback** | Restore previous registry |

#### Phase F: Register Tools

| Aspect | Specification |
|--------|---------------|
| **Inputs** | Phase E complete, tool verification |
| **Scripts** | `register_tools_batch_v0_1.py` |
| **Files Created** | Updated `REGISTRY/ARSENAL_TOOL_INDEX.json`, `REGISTRY/ARSENAL_INSTALL_STATUS.json` |
| **Checks** | All known tools registered, install status verified |
| **Pass Criteria** | Tool coverage ≥ 80% |
| **Risks** | Incorrect install status |
| **Rollback** | Restore previous registry |

#### Phase G: Build Dashboards

| Aspect | Specification |
|--------|---------------|
| **Inputs** | Phase E, F registries |
| **Scripts** | `build_backend_health_dashboard_data_v0_1.py` |
| **Files Created** | `SANCTUM/DASHBOARD/DATA/*.json` |
| **Checks** | Dashboard data valid, no fake green |
| **Pass Criteria** | All dashboards have data, truth coverage ≥ 80% |
| **Risks** | Stale data |
| **Rollback** | Regenerate data |

#### Phase H: Quarantine Trash

| Aspect | Specification |
|--------|---------------|
| **Inputs** | Phase D classification (UNKNOWN_ORPHAN, TEMPORARY_WORK) |
| **Scripts** | `quarantine_files_v0_1.py` |
| **Files Created** | Files moved to `QUARANTINE/`, manifest created |
| **Checks** | Only classified trash moved, manifest accurate |
| **Pass Criteria** | Quarantine manifest matches moved files |
| **Risks** | Moving legitimate files |
| **Rollback** | Move files back from quarantine |

#### Phase I: Update .gitignore

| Aspect | Specification |
|--------|---------------|
| **Inputs** | Phase D classification (SHOULD_NOT_TRACK, PRIVATE_LOCAL_ONLY) |
| **Scripts** | `update_gitignore_v0_1.py` |
| **Files Created** | Updated `.gitignore` |
| **Checks** | All temp/private patterns covered |
| **Pass Criteria** | `git status` shows no untracked temp files |
| **Risks** | Over-ignoring legitimate files |
| **Rollback** | Restore previous .gitignore |

#### Phase J: Add Regression Checks

| Aspect | Specification |
|--------|---------------|
| **Inputs** | All previous phases |
| **Scripts** | `check_backend_truth_spine_v0_1.py` |
| **Files Created** | New checker script, test cases |
| **Checks** | Checker runs without error, catches known issues |
| **Pass Criteria** | Checker passes on clean state, fails on dirty state |
| **Risks** | False positives/negatives |
| **Rollback** | Disable checker |

#### Phase K: Freeze Cleaned Baseline

| Aspect | Specification |
|--------|---------------|
| **Inputs** | All previous phases complete |
| **Scripts** | Manual commit |
| **Files Created** | Git commit |
| **Checks** | All checkers pass, no blockers |
| **Pass Criteria** | Clean commit with evidence |
| **Risks** | Committing incomplete cleanup |
| **Rollback** | `git reset --hard HEAD~1` |

---

## SECTION 12 — CONCRETE FILE TREE PROPOSAL

### 12.1 Proposed Structure

```
E:\IMPERIUM\
├── .gitignore                          # [UPDATE] Add new patterns
├── .gitattributes                      # [EXISTS]
├── AGENTS.md                           # [EXISTS]
├── README.md                           # [EXISTS]
├── START_HERE.md                       # [EXISTS]
│
├── REGISTRY/                           # [Git tracked]
│   ├── SCRIPT_REGISTRY.json            # [UPDATE] Expand coverage
│   ├── ARSENAL_TOOL_INDEX.json         # [UPDATE] Add missing tools
│   ├── ARSENAL_INSTALL_STATUS.json     # [EXISTS]
│   ├── ERROR_REGISTRY.json             # [CREATE] Script error tracking
│   ├── ORPHAN_FILE_REGISTRY.json       # [CREATE] Unclassified files
│   ├── BUNDLE_ROUTE_REGISTRY.json      # [EXISTS]
│   ├── WARNING_BUDGET.json             # [EXISTS]
│   └── ...
│
├── TOOLS/                              # [Git tracked]
│   ├── inventory_repo_truth_v0_1.py    # [CREATE]
│   ├── build_scriptorium_registry_v0_1.py  # [CREATE]
│   ├── check_scriptorium_registry_v0_1.py  # [CREATE]
│   ├── build_arsenal_registry_v0_1.py  # [CREATE]
│   ├── check_arsenal_registry_v0_1.py  # [EXISTS]
│   ├── build_backend_health_dashboard_data_v0_1.py  # [CREATE]
│   ├── check_backend_truth_spine_v0_1.py  # [CREATE]
│   ├── record_script_error_v0_1.py     # [CREATE]
│   ├── bundle_fetch_review_v0_1.py     # [CREATE]
│   ├── bundle_apply_commit_v0_1.py     # [CREATE]
│   ├── vm2_exact_sync_v0_1.py          # [CREATE]
│   ├── detect_orphan_files_v0_1.py     # [CREATE]
│   ├── classify_repo_files_v0_1.py     # [CREATE]
│   └── ... (existing scripts)
│
├── scripts/                            # [Git tracked]
│   └── ... (existing scripts)
│
├── schemas/                            # [Git tracked]
│   ├── script_registry.schema.json     # [EXISTS]
│   ├── arsenal_tool.schema.json        # [EXISTS]
│   ├── error_registry.schema.json      # [CREATE]
│   ├── file_taxonomy.schema.json       # [CREATE]
│   ├── dashboard_data.schema.json      # [CREATE]
│   └── ...
│
├── ORGANS/
│   └── MECHANICUS/                     # [Git tracked]
│       ├── ORGAN_CONTRACT.json         # [CREATE]
│       ├── ORGAN_STATUS.json           # [EXISTS]
│       ├── SELF_REPORT.json            # [CREATE]
│       ├── README.md                   # [EXISTS]
│       ├── SCRIPT_REPAIR_POLICY.md     # [CREATE]
│       ├── ERROR_LEARNING_POLICY.md    # [CREATE]
│       ├── FUNDAMENTAL_SCRIPT_STANDARD.md  # [CREATE]
│       ├── BACKEND_BRIDGE_POLICY.md    # [CREATE]
│       ├── LAUNCHER_STANDARD.md        # [CREATE]
│       └── REGISTRY/
│           ├── ERROR_REGISTRY.json     # [CREATE] Local error tracking
│           └── REPAIR_LOG.json         # [CREATE]
│
├── SANCTUM/
│   └── DASHBOARD/                      # [Git tracked]
│       ├── DATA/                       # [.gitignore] Generated data
│       │   ├── scriptorium.json
│       │   ├── arsenal.json
│       │   ├── sanctum_truth.json
│       │   └── backend_health.json
│       ├── TEMPLATES/                  # [Git tracked] Dashboard templates
│       └── README.md
│
├── CURRENT_STATE/                      # [Git tracked]
│   └── ... (existing)
│
├── INBOX/                              # [.gitignore]
│   ├── VM2_BUNDLES/
│   ├── VM2_REVIEW/
│   ├── QUARANTINE/
│   └── UPLOADED_SUPPLEMENTS/
│
├── QUARANTINE/                         # [.gitignore] Cleanup quarantine
│   ├── MANIFEST.json
│   └── ... (quarantined files)
│
├── .imperium_runtime/                  # [.gitignore]
│   ├── cleanup/                        # Cleanup phase outputs
│   ├── scriptorium/                    # Script registry checks
│   ├── arsenal/                        # Tool registry checks
│   ├── dashboard/                      # Dashboard build outputs
│   ├── mechanicus/                     # MECHANICUS runtime
│   │   └── errors/                     # Error captures
│   ├── bundles/                        # Bundle staging
│   ├── bundle_intake_review/           # Review sessions
│   ├── vm2_sync/                       # VM2 sync receipts
│   └── verification_spine/             # verify_repo.py outputs
│
├── BUNDLES_LOCAL/                      # [.gitignore]
├── CHAT_COMPILATIONS_LOCAL/            # [.gitignore]
├── PRIVATE_CONTEXT_LOCAL/              # [.gitignore]
└── RUNTIME_LOCAL/                      # [.gitignore]
```

### 12.2 Tracking Policy Summary

| Path Pattern | Tracking |
|--------------|----------|
| `REGISTRY/*.json` | Git tracked |
| `TOOLS/*.py`, `TOOLS/*.ps1` | Git tracked |
| `scripts/*.py` | Git tracked |
| `schemas/*.json` | Git tracked |
| `ORGANS/*/ORGAN_CONTRACT.json` | Git tracked |
| `ORGANS/*/ORGAN_STATUS.json` | Git tracked |
| `SANCTUM/DASHBOARD/DATA/` | .gitignore |
| `INBOX/` | .gitignore |
| `QUARANTINE/` | .gitignore |
| `.imperium_runtime/` | .gitignore |
| `*_LOCAL/` | .gitignore |
| `__pycache__/` | .gitignore |

---

## SECTION 13 — CONCRETE SCRIPT PROPOSALS

### 13.1 First Wave Scripts

| Script | Purpose | Inputs | Outputs | Side Effects | Safety | Status |
|--------|---------|--------|---------|--------------|--------|--------|
| `inventory_repo_truth_v0_1.py` | Snapshot current repo state | repo root | JSON report | None | Safe | CREATE |
| `build_scriptorium_registry_v0_1.py` | Scan and register scripts | repo root, existing registry | Updated registry | Modifies registry | Safe | CREATE |
| `check_scriptorium_registry_v0_1.py` | Validate script registry | registry path | Verdict + receipt | Runtime only | Safe | CREATE |
| `build_arsenal_registry_v0_1.py` | Scan and register tools | repo root, existing registry | Updated registry | Modifies registry | Safe | CREATE |
| `check_arsenal_registry_v0_1.py` | Validate tool registry | registry path | Verdict + receipt | Runtime only | Safe | EXISTS |
| `build_backend_health_dashboard_data_v0_1.py` | Build dashboard data | repo root | Dashboard JSON | Runtime only | Safe | CREATE |
| `check_backend_truth_spine_v0_1.py` | Validate backend health | repo root | Verdict + receipt | Runtime only | Safe | CREATE |
| `record_script_error_v0_1.py` | Record script failure | error details | Error registry entry | Modifies registry | Safe | CREATE |
| `bundle_fetch_review_v0_1.py` | Fetch and review bundle | source, task | Bundle + report | Network, writes INBOX | Safe | CREATE |
| `bundle_apply_commit_v0_1.py` | Apply bundle and commit | bundle path, task | Commit | Modifies repo | Owner approval | CREATE |
| `vm2_exact_sync_v0_1.py` | Sync VM2 to PC HEAD | target | Sync report | Network, VM2 git | Owner approval | CREATE |

### 13.2 Script Specifications

#### `inventory_repo_truth_v0_1.py`

```
Purpose: Capture complete snapshot of current repo state for cleanup baseline
Inputs: --repo-root
Outputs: 
  - .imperium_runtime/cleanup/REPO_TRUTH_INVENTORY.json
  - .imperium_runtime/cleanup/REPO_TRUTH_INVENTORY_RECEIPT.json
Side Effects: Writes to .imperium_runtime only
Safety: Safe (read-only scan)
Receipt: Yes
Dashboard: Provides baseline for all metrics
```

#### `build_scriptorium_registry_v0_1.py`

```
Purpose: Scan TOOLS/ and scripts/ and generate/update SCRIPT_REGISTRY.json
Inputs: --repo-root, --existing-registry (optional)
Outputs:
  - REGISTRY/SCRIPT_REGISTRY.json (updated)
  - .imperium_runtime/scriptorium/BUILD_REGISTRY_RECEIPT.json
Side Effects: Modifies REGISTRY/SCRIPT_REGISTRY.json
Safety: Safe (additive only, preserves existing entries)
Receipt: Yes
Dashboard: Updates SCRIPTORIUM dashboard data
```

#### `check_backend_truth_spine_v0_1.py`

```
Purpose: Comprehensive backend health check combining all metrics
Inputs: --repo-root
Outputs:
  - .imperium_runtime/backend_health/BACKEND_TRUTH_SPINE_RESULT.json
  - .imperium_runtime/backend_health/BACKEND_TRUTH_SPINE_VERDICT.md
  - .imperium_runtime/backend_health/BACKEND_TRUTH_SPINE_RECEIPT.json
Side Effects: Writes to .imperium_runtime only
Safety: Safe (read-only checks)
Receipt: Yes
Dashboard: Primary data source for Backend Health Dashboard
Exit Codes: 0 = PASS, 1 = PASS_WITH_WARNINGS, 2 = BLOCKED
```

---

## SECTION 14 — EXAMPLE CODE

### 14.1 Python Repo Inventory Scanner

```python
#!/usr/bin/env python3
"""inventory_repo_truth_v0_1.py - Capture repo state snapshot."""

import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

def get_git_info(repo_root: Path) -> Dict[str, Any]:
    """Get current git state."""
    def run_git(args: List[str]) -> str:
        result = subprocess.run(
            ["git"] + args,
            cwd=repo_root,
            capture_output=True,
            text=True
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    
    return {
        "head": run_git(["rev-parse", "HEAD"]),
        "branch": run_git(["rev-parse", "--abbrev-ref", "HEAD"]),
        "commit_count": int(run_git(["rev-list", "--count", "HEAD"]) or 0),
        "last_commit_subject": run_git(["log", "-1", "--format=%s"]),
        "dirty": bool(run_git(["status", "--porcelain"]))
    }

def scan_scripts(repo_root: Path) -> Dict[str, List[Dict]]:
    """Scan for all script files."""
    scripts = {"python": [], "powershell": [], "bash": []}
    
    for pattern, category in [("**/*.py", "python"), ("**/*.ps1", "powershell"), ("**/*.sh", "bash")]:
        for path in repo_root.glob(pattern):
            if ".git" in path.parts or "__pycache__" in path.parts:
                continue
            scripts[category].append({
                "path": str(path.relative_to(repo_root)),
                "size_bytes": path.stat().st_size,
                "modified_at": datetime.fromtimestamp(
                    path.stat().st_mtime, tz=timezone.utc
                ).isoformat()
            })
    
    return scripts

Продолжаю с Section 14 — Example Code.

---

### 14.1 Python Repo Inventory Scanner (продолжение)

```python
def build_inventory(repo_root: Path) -> Dict[str, Any]:
    """Build complete repo inventory."""
    return {
        "schema_version": "imperium.repo_inventory.v0_1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "git": get_git_info(repo_root),
        "scripts": scan_scripts(repo_root),
        "file_counts": {
            "total_tracked": len(list(repo_root.glob("**/*"))),
            "python_scripts": sum(1 for _ in repo_root.glob("**/*.py") 
                                  if ".git" not in _.parts),
            "powershell_scripts": sum(1 for _ in repo_root.glob("**/*.ps1")),
            "json_files": sum(1 for _ in repo_root.glob("**/*.json") 
                              if ".git" not in _.parts)
        }
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Inventory repo truth")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--json-out", help="Output JSON path")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    inventory = build_inventory(repo_root)
    
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(inventory, indent=2))
    
    if args.human:
        print(f"Repository: {inventory['repo_root']}")
        print(f"HEAD: {inventory['git']['head'][:12]}")
        print(f"Commit count: {inventory['git']['commit_count']}")
        print(f"Python scripts: {inventory['file_counts']['python_scripts']}")
        print(f"PowerShell scripts: {inventory['file_counts']['powershell_scripts']}")
```

### 14.2 Script Registry Entry Generator

```python
#!/usr/bin/env python3
"""Generate SCRIPTORIUM registry entry for a script."""

import json
import ast
from pathlib import Path
from typing import Dict, Any, Optional

def extract_docstring(script_path: Path) -> Optional[str]:
    """Extract module docstring from Python script."""
    if script_path.suffix != ".py":
        return None
    try:
        tree = ast.parse(script_path.read_text(encoding="utf-8"))
        return ast.get_docstring(tree)
    except:
        return None

def detect_platform(script_path: Path) -> str:
    """Detect script platform from extension and content."""
    suffix = script_path.suffix.lower()
    if suffix == ".ps1":
        return "WINDOWS_ONLY"
    elif suffix == ".sh":
        return "UBUNTU_ONLY"
    elif suffix == ".py":
        content = script_path.read_text(encoding="utf-8", errors="ignore")
        if "subprocess.run" in content and "powershell" in content.lower():
            return "WINDOWS_ONLY"
        return "CROSS_PLATFORM"
    return "UNKNOWN"

def detect_side_effects(script_path: Path) -> list:
    """Detect potential side effects from script content."""
    content = script_path.read_text(encoding="utf-8", errors="ignore")
    effects = []
    
    if any(x in content for x in ["open(", "write(", "Path(", ".write_text"]):
        if ".imperium_runtime" in content:
            effects.append("WRITES_RUNTIME_ONLY")
        else:
            effects.append("MODIFIES_REPO")
    
    if any(x in content for x in ["subprocess", "os.system", "Popen"]):
        effects.append("EXECUTES_COMMANDS")
    
    if any(x in content for x in ["requests.", "urllib", "socket", "ssh", "scp"]):
        effects.append("NETWORK_ACCESS")
    
    if not effects:
        effects.append("SAFE_READONLY")
    
    return effects

def generate_registry_entry(script_path: Path, owner_organ: str = "UNKNOWN") -> Dict[str, Any]:
    """Generate a SCRIPTORIUM registry entry."""
    name = script_path.name
    script_id = f"SCRIPT-{name.upper().replace('.', '-').replace('_', '-')}"
    
    docstring = extract_docstring(script_path)
    purpose = docstring.split('\n')[0] if docstring else f"Script: {name}"
    
    platform = detect_platform(script_path)
    side_effects = detect_side_effects(script_path)
    
    runtime_map = {".py": "PYTHON3", ".ps1": "POWERSHELL", ".sh": "BASH"}
    runtime = runtime_map.get(script_path.suffix.lower(), "UNKNOWN")
    
    return {
        "script_id": script_id,
        "path": str(script_path),
        "name": name,
        "owner_organ": owner_organ,
        "support_layer": "SCRIPTORIUM",
        "purpose": purpose[:200],
        "platform": platform,
        "runtime": runtime,
        "entrypoint_command": f"python3 {script_path}" if runtime == "PYTHON3" else f"powershell -File {script_path}",
        "required_args": [],
        "optional_args": [],
        "reads": [],
        "writes": [],
        "side_effects": side_effects,
        "produces_receipts": "WRITES_RUNTIME_ONLY" in side_effects,
        "receipt_paths": [],
        "modifies_repo": "MODIFIES_REPO" in side_effects,
        "safe_for_servitor": "SAFE_READONLY" in side_effects or "WRITES_RUNTIME_ONLY" in side_effects,
        "dangerous_if_misused": "MODIFIES_REPO" in side_effects or "NETWORK_ACCESS" in side_effects,
        "known_dependencies": ["python3"] if runtime == "PYTHON3" else ["powershell"],
        "expected_exit_codes": [0],
        "status": "CANDIDATE",
        "last_verified_at": None
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python generate_registry_entry.py <script_path> [owner_organ]")
        sys.exit(1)
    
    script_path = Path(sys.argv[1])
    owner = sys.argv[2] if len(sys.argv) > 2 else "UNKNOWN"
    
    entry = generate_registry_entry(script_path, owner)
    print(json.dumps(entry, indent=2))
```

### 14.3 Tool Availability Checker

```python
#!/usr/bin/env python3
"""Check tool availability and version."""

import subprocess
import json
from typing import Dict, Any, Optional

TOOL_CHECKS = {
    "git": {"command": ["git", "--version"], "parse": lambda x: x.split()[-1]},
    "python3": {"command": ["python3", "--version"], "parse": lambda x: x.split()[-1]},
    "ssh": {"command": ["ssh", "-V"], "parse": lambda x: x.split()[0]},
    "powershell": {"command": ["powershell", "-Command", "$PSVersionTable.PSVersion.ToString()"], "parse": lambda x: x.strip()},
}

def check_tool(tool_id: str) -> Dict[str, Any]:
    """Check if a tool is available and get its version."""
    if tool_id not in TOOL_CHECKS:
        return {"tool_id": tool_id, "available": False, "error": "Unknown tool"}
    
    check = TOOL_CHECKS[tool_id]
    try:
        result = subprocess.run(
            check["command"],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout or result.stderr
        version = check["parse"](output) if output else "unknown"
        
        return {
            "tool_id": tool_id,
            "available": result.returncode == 0,
            "version": version,
            "command": " ".join(check["command"]),
            "exit_code": result.returncode
        }
    except FileNotFoundError:
        return {"tool_id": tool_id, "available": False, "error": "Not found"}
    except subprocess.TimeoutExpired:
        return {"tool_id": tool_id, "available": False, "error": "Timeout"}
    except Exception as e:
        return {"tool_id": tool_id, "available": False, "error": str(e)}

def check_all_tools() -> Dict[str, Any]:
    """Check all registered tools."""
    results = {}
    for tool_id in TOOL_CHECKS:
        results[tool_id] = check_tool(tool_id)
    return results

if __name__ == "__main__":
    results = check_all_tools()
    print(json.dumps(results, indent=2))
```

### 14.4 Error Event Recorder

```python
#!/usr/bin/env python3
"""record_script_error_v0_1.py - Record script failure to error registry."""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

def generate_error_id() -> str:
    """Generate unique error ID."""
    now = datetime.now(timezone.utc)
    return f"ERR-{now.strftime('%Y%m%d-%H%M%S')}-{now.microsecond:06d}"

def record_error(
    script_id: str,
    script_path: str,
    command_used: str,
    exit_code: int,
    stdout: str,
    stderr: str,
    error_message: str,
    severity: str = "MEDIUM",
    error_type: str = "UNKNOWN",
    suspected_cause: str = "",
    repo_root: Path = Path(".")
) -> Dict[str, Any]:
    """Record a script error to the error registry."""
    
    error_entry = {
        "error_id": generate_error_id(),
        "script_id": script_id,
        "script_path": script_path,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "severity": severity,
        "error_type": error_type,
        "command_used": command_used,
        "working_directory": str(Path.cwd()),
        "environment": {
            "platform": sys.platform,
            "python_version": sys.version.split()[0]
        },
        "exit_code": exit_code,
        "stdout_capture": stdout[:2000] if stdout else "",
        "stderr_capture": stderr[:2000] if stderr else "",
        "error_message": error_message,
        "suspected_cause": suspected_cause,
        "reproducibility": "UNKNOWN",
        "status": "NEW",
        "repair_decision": None,
        "regression_test_required": False
    }
    
    # Write to error registry
    registry_path = repo_root / "ORGANS" / "MECHANICUS" / "REGISTRY" / "ERROR_REGISTRY.json"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    
    if registry_path.exists():
        registry = json.loads(registry_path.read_text())
    else:
        registry = {"schema_version": "imperium.error_registry.v0_1", "errors": []}
    
    registry["errors"].append(error_entry)
    registry["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    registry_path.write_text(json.dumps(registry, indent=2))
    
    return error_entry

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Record script error")
    parser.add_argument("--script-id", required=True)
    parser.add_argument("--script-path", required=True)
    parser.add_argument("--command", required=True)
    parser.add_argument("--exit-code", type=int, required=True)
    parser.add_argument("--stdout", default="")
    parser.add_argument("--stderr", default="")
    parser.add_argument("--error-message", required=True)
    parser.add_argument("--severity", default="MEDIUM")
    parser.add_argument("--error-type", default="UNKNOWN")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    
    entry = record_error(
        script_id=args.script_id,
        script_path=args.script_path,
        command_used=args.command,
        exit_code=args.exit_code,
        stdout=args.stdout,
        stderr=args.stderr,
        error_message=args.error_message,
        severity=args.severity,
        error_type=args.error_type,
        repo_root=Path(args.repo_root)
    )
    
    print(f"Recorded error: {entry['error_id']}")
```

### 14.5 Dashboard Data Builder Skeleton

```python
#!/usr/bin/env python3
"""build_backend_health_dashboard_data_v0_1.py - Build dashboard data."""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

def load_json_safe(path: Path) -> Dict[str, Any]:
    """Load JSON file safely, return empty dict on error."""
    try:
        return json.loads(path.read_text()) if path.exists() else {}
    except:
        return {"_error": f"Failed to load {path}"}

def calculate_script_coverage(repo_root: Path) -> Dict[str, Any]:
    """Calculate script registration coverage."""
    registry_path = repo_root / "REGISTRY" / "SCRIPT_REGISTRY.json"
    registry = load_json_safe(registry_path)
    
    registered_paths = set()
    for script in registry.get("scripts", []):
        if script.get("path") and script.get("status") != "BLOCKED":
            registered_paths.add(script["path"])
    
    # Count actual scripts
    actual_scripts = set()
    for folder in ["TOOLS", "scripts"]:
        folder_path = repo_root / folder
        if folder_path.exists():
            for ext in ["*.py", "*.ps1", "*.sh"]:
                for f in folder_path.glob(ext):
                    actual_scripts.add(str(f.relative_to(repo_root)))
    
    coverage = len(registered_paths & actual_scripts) / len(actual_scripts) * 100 if actual_scripts else 0
    
    return {
        "registered_count": len(registered_paths),
        "actual_count": len(actual_scripts),
        "coverage_percent": round(coverage, 1),
        "unregistered": list(actual_scripts - registered_paths)[:10],
        "status": "PASS" if coverage >= 90 else "WARNING" if coverage >= 70 else "BLOCKED"
    }

def build_dashboard_data(repo_root: Path) -> Dict[str, Any]:
    """Build complete backend health dashboard data."""
    return {
        "schema_version": "imperium.dashboard_data.v0_1",
        "dashboard_id": "backend-health",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "panels": {
            "script_coverage": calculate_script_coverage(repo_root),
            # Add more panels here
        },
        "overall_status": "PASS_WITH_WARNINGS",  # Calculate from panels
        "warnings": [],
        "blockers": []
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json-out")
    parser.add_argument("--human", action="store_true")
    args = parser.parse_args()
    
    data = build_dashboard_data(Path(args.repo_root))
    
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(json.dumps(data, indent=2))
    
    if args.human:
        sc = data["panels"]["script_coverage"]
        print(f"Script Coverage: {sc['coverage_percent']}% ({sc['registered_count']}/{sc['actual_count']})")
        print(f"Status: {sc['status']}")
        if sc["unregistered"]:
            print(f"Unregistered (first 10): {', '.join(sc['unregistered'])}")
```

### 14.6 Checker That Fails on Unregistered Scripts

```python
#!/usr/bin/env python3
"""check_scriptorium_registry_v0_1.py - Fail if unregistered scripts exist."""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

def check_scriptorium(repo_root: Path) -> dict:
    """Check script registration coverage."""
    registry_path = repo_root / "REGISTRY" / "SCRIPT_REGISTRY.json"
    
    if not registry_path.exists():
        return {"verdict": "BLOCKED", "reason": "SCRIPT_REGISTRY.json not found"}
    
    registry = json.loads(registry_path.read_text())
    registered = {s["path"] for s in registry.get("scripts", []) if s.get("path")}
    
    # Scan actual scripts
    actual = set()
    for folder in ["TOOLS", "scripts"]:
        folder_path = repo_root / folder
        if folder_path.exists():
            for ext in ["*.py", "*.ps1", "*.sh"]:
                for f in folder_path.glob(ext):
                    rel = str(f.relative_to(repo_root)).replace("\\", "/")
                    actual.add(rel)
    
    unregistered = actual - registered
    coverage = (len(actual) - len(unregistered)) / len(actual) * 100 if actual else 100
    
    result = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "total_scripts": len(actual),
        "registered_scripts": len(actual) - len(unregistered),
        "unregistered_scripts": len(unregistered),
        "coverage_percent": round(coverage, 1),
        "unregistered_list": sorted(unregistered)
    }
    
    if coverage >= 90:
        result["verdict"] = "PASS"
    elif coverage >= 70:
        result["verdict"] = "PASS_WITH_WARNINGS"
        result["warnings"] = [f"Coverage {coverage}% < 90%"]
    else:
        result["verdict"] = "BLOCKED"
        result["blockers"] = [f"Coverage {coverage}% < 70%"]
    
    return result

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--human", action="store_true")
    parser.add_argument("--json-out")
    args = parser.parse_args()
    
    result = check_scriptorium(Path(args.repo_root))
    
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(result, indent=2))
    
    if args.human:
        print(f"SCRIPTORIUM Check: {result['verdict']}")
        print(f"Coverage: {result['coverage_percent']}%")
        print(f"Registered: {result['registered_scripts']}/{result['total_scripts']}")
        if result["unregistered_list"]:
            print(f"Unregistered ({len(result['unregistered_list'])}):")
            for s in result["unregistered_list"][:10]:
                print(f"  - {s}")
    
    # Exit code based on verdict
    exit_codes = {"PASS": 0, "PASS_WITH_WARNINGS": 0, "BLOCKED": 2}
    sys.exit(exit_codes.get(result["verdict"], 1))
```

---

## SECTION 15 — WARNINGS / ANTI-PATTERNS

### 15.1 What IMPERIUM Must Stop Doing

| Anti-Pattern | Why It's Dangerous | Replacement |
|--------------|-------------------|-------------|
| **Huge one-off chat commands** | No versioning, no receipts, no learning | Registered launcher scripts |
| **Unregistered scripts** | No tracking, no reliability data | SCRIPTORIUM registration |
| **Untracked bundles in random folders** | Lost provenance, no cleanup | Canonical INBOX/OUTBOX paths |
| **Dashboards with fake buttons** | False confidence, broken UX | Disabled buttons until bridge exists |
| **Accepting advisory as canon** | Advisory is input, not doctrine | Explicit reconciliation workflow |
| **Calling task ready when warnings unknown** | Fake green | Warning classification required |
| **Mixing apply/commit/sync in one-shot** | Fragile, no rollback | Separate modes with dry-run |
| **Deleting dirt without quarantine** | Data loss, no recovery | Quarantine with TTL |
| **Tracking private/local-only data** | Security risk, repo pollution | .gitignore enforcement |
| **Copy-pasting commands between sessions** | Drift, no version control | Registered scripts with versions |
| **Ignoring script errors** | Same errors repeat | Error registry + learning loop |
| **Assuming tool availability** | Runtime failures | ARSENAL verification |
| **Manual file classification** | Inconsistent, slow | Automated taxonomy checker |
| **Undocumented scripts** | Agent confusion | Mandatory purpose field |

### 15.2 Specific Forbidden Patterns

```
❌ FORBIDDEN:
ssh user@vm2 "cd /path && git fetch && git reset --hard origin/master && ..."

✓ REQUIRED:
python3 TOOLS/vm2_exact_sync_v0_1.py --target vm2 --mode verify --dry-run
python3 TOOLS/vm2_exact_sync_v0_1.py --target vm2 --mode sync
```

```
❌ FORBIDDEN:
powershell -Command "... 50 lines of inline script ..."

✓ REQUIRED:
python3 TOOLS/bundle_fetch_review_v0_1.py --source vm2 --task TASK-XXX --mode review
```

```
❌ FORBIDDEN:
# Dashboard button that does nothing
<button onclick="alert('Not implemented')">Apply Bundle</button>

✓ REQUIRED:
# Button disabled with clear reason
<button disabled title="Requires backend bridge">Apply Bundle</button>
```

---

## SECTION 16 — RECOMMENDED NEXT 5 TASKS

### Task 1: TASK-20260513-SAN-CLEANING-CURRENT-TRUTH-INVENTORY-V0_1

| Aspect | Specification |
|--------|---------------|
| **Goal** | Capture complete baseline of current repo state |
| **Files to Create** | `TOOLS/inventory_repo_truth_v0_1.py` |
| **Files to Update** | None |
| **Scripts/Checkers** | New inventory script |
| **Pass Criteria** | Inventory JSON generated with all metrics, no scan errors |
| **Expected Risk** | LOW — read-only operation |

### Task 2: TASK-20260513-SCRIPTORIUM-REGISTRY-EXPANSION-V0_1

| Aspect | Specification |
|--------|---------------|
| **Goal** | Register all scripts in TOOLS/ and scripts/ |
| **Files to Create** | `TOOLS/build_scriptorium_registry_v0_1.py`, `TOOLS/check_scriptorium_registry_v0_1.py` |
| **Files to Update** | `REGISTRY/SCRIPT_REGISTRY.json` |
| **Scripts/Checkers** | Registry builder + checker |
| **Pass Criteria** | Coverage ≥ 90%, checker passes |
| **Expected Risk** | LOW — additive registry changes |

### Task 3: TASK-20260513-MECHANICUS-ORGAN-CONTRACT-V0_1

| Aspect | Specification |
|--------|---------------|
| **Goal** | Create MECHANICUS ORGAN_CONTRACT.json and supporting policies |
| **Files to Create** | `ORGANS/MECHANICUS/ORGAN_CONTRACT.json`, `ORGANS/MECHANICUS/SELF_REPORT.json`, `ORGANS/MECHANICUS/SCRIPT_REPAIR_POLICY.md`, `ORGANS/MECHANICUS/ERROR_LEARNING_POLICY.md` |
| **Files to Update** | `ORGANS/MECHANICUS/ORGAN_STATUS.json` |
| **Scripts/Checkers** | Organ contract checker |
| **Pass Criteria** | Contract validates against schema, status updated |
| **Expected Risk** | LOW — documentation only |

### Task 4: TASK-20260513-ERROR-REGISTRY-AND-LEARNING-LOOP-V0_1

| Aspect | Specification |
|--------|---------------|
| **Goal** | Create error registry schema and recorder script |
| **Files to Create** | `schemas/error_registry.schema.json`, `TOOLS/record_script_error_v0_1.py`, `ORGANS/MECHANICUS/REGISTRY/ERROR_REGISTRY.json` |
| **Files to Update** | `REGISTRY/SCRIPT_REGISTRY.json` (add new script) |
| **Scripts/Checkers** | Error recorder |
| **Pass Criteria** | Error can be recorded and retrieved, schema validates |
| **Expected Risk** | LOW — new capability, no breaking changes |

### Task 5: TASK-20260513-BACKEND-HEALTH-DASHBOARD-DATA-V0_1

| Aspect | Specification |
|--------|---------------|
| **Goal** | Create backend health dashboard data builder |
| **Files to Create** | `TOOLS/build_backend_health_dashboard_data_v0_1.py`, `TOOLS/check_backend_truth_spine_v0_1.py`, `schemas/dashboard_data.schema.json` |
| **Files to Update** | `REGISTRY/SCRIPT_REGISTRY.json` |
| **Scripts/Checkers** | Dashboard builder + truth spine checker |
| **Pass Criteria** | Dashboard data generated, all metrics have values, checker passes |
| **Expected Risk** | LOW — read-only data generation |

---

## SECTION 17 — MINIMAL FIRST IMPLEMENTATION SLICE

### What Can Be Done in One Safe Commit

The smallest safe first slice that gives IMPERIUM immediate value:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MINIMAL FIRST IMPLEMENTATION SLICE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. CREATE: TOOLS/inventory_repo_truth_v0_1.py                              │
│     - Scans repo, counts files, captures git state                          │
│     - Outputs JSON inventory                                                │
│     - ~100 lines of Python                                                  │
│                                                                             │
│  2. CREATE: TOOLS/check_scriptorium_registry_v0_1.py                        │
│     - Compares SCRIPT_REGISTRY.json with actual files                       │
│     - Reports coverage percentage                                           │
│     - Lists unregistered scripts                                            │
│     - ~80 lines of Python                                                   │
│                                                                             │
│  3. UPDATE: REGISTRY/SCRIPT_REGISTRY.json                                   │
│     - Add entries for 19 unregistered scripts in TOOLS/                     │
│     - Status: CANDIDATE for new entries                                     │
│     - Increases coverage from ~60% to ~95%                                  │
│                                                                             │
│  4. CREATE: ORGANS/MECHANICUS/ORGAN_CONTRACT.json                           │
│     - Formal contract for MECHANICUS organ                                  │
│     - Defines ownership of SCRIPTORIUM/ARSENAL                              │
│     - ~50 lines of JSON                                                     │
│                                                                             │
│  5. CREATE: schemas/error_registry.schema.json                              │
│     - Schema for script error tracking                                      │
│     - Enables future error learning loop                                    │
│     - ~100 lines of JSON schema                                             │
│                                                                             │
│  6. RUN: verify_repo.py + new checkers                                      │
│     - Verify no regressions                                                 │
│     - Capture evidence                                                      │
│                                                                             │
│  NO DELETION in this slice.                                                 │
│  NO QUARANTINE in this slice.                                               │
│  NO DASHBOARD CHANGES in this slice.                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Expected Outcomes

| Metric | Before | After |
|--------|--------|-------|
| Script registration coverage | ~60% | ~95% |
| MECHANICUS ORGAN_CONTRACT | Missing | Created |
| Error registry schema | Missing | Created |
| Inventory capability | None | Operational |
| Scriptorium checker | None | Operational |

### Commit Message Template

```
TASK-20260513: san-cleaning minimal first slice — scriptorium expansion and mechanicus contract

- Add inventory_repo_truth_v0_1.py for repo state capture
- Add check_scriptorium_registry_v0_1.py for coverage validation
- Expand SCRIPT_REGISTRY.json with 19 new entries (coverage 60% → 95%)
- Create ORGANS/MECHANICUS/ORGAN_CONTRACT.json
- Add schemas/error_registry.schema.json for future error learning

No deletions. No quarantine. Registry expansion only.
```

---

## FINAL SUMMARY

### Advisory Verdict

**IMPERIUM is slowing down because:**
1. Script registration coverage is insufficient (~60%)
2. Ad hoc PowerShell commands have no receipts or learning
3. MECHANICUS organ is not operational (no contract)
4. No error registry exists — same mistakes repeat
5. Warning flood masks real problems
6. File taxonomy is not enforced

**The fix requires:**
1. SCRIPTORIUM expansion to ≥90% coverage
2. MECHANICUS ORGAN_CONTRACT.json creation
3. Error registry and learning loop
4. Registered launcher scripts replacing ad hoc commands
5. Backend health dashboard with truth guarantees
6. Phased cleanup with quarantine (no deletion)

**Minimal first slice delivers:**
- Inventory capability
- Scriptorium checker
- Registry expansion
- MECHANICUS contract
- Error registry schema

**This is an advisory architecture plan, not an execution report.**

No files have been created or modified.
No claims of completion are made.
Owner approval required before execution.

---

```
╔══════════════════════════════════════════════════════════════════════════════╗
║           END OF SAN-CLEANING / BACKEND TRUTH ADVISORY PACK                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  TASK_ID: TASK-20260513-SAN-CLEANING-BACKEND-TRUTH-SCRIPTORIUM-ARSENAL-     ║
║           MECHANICUS-V0_1                                                    ║
║  HEAD:    efe74dd0abf7d5b11ef305876832db1f827bcdb4                           ║
║  DATE:    2026-05-13                                                         ║
║  MODE:    Advisory architecture — no execution                               ║
║  STATUS:  DELIVERED — awaiting Owner review                                  ║
╚══════════════
