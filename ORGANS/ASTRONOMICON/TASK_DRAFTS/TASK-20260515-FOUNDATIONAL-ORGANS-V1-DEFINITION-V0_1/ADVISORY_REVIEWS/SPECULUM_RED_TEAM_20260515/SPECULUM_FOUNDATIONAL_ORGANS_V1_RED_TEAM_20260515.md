# SPECULUM RED-TEAM REPORT — FOUNDATIONAL ORGANS V1

Report file: `SPECULUM_FOUNDATIONAL_ORGANS_V1_RED_TEAM_20260515.md`  
Project: `IMPERIUM`  
Review role: `Logos-Speculum`  
Review mode: hard red-team architecture review  
Review target: Owner-readable V1 prefill matrix and first-four foundational organs V1 hardening plan  
Verified Git HEAD under review: `931940980288cd42ece295d1107633d1fc55abf2`  
Verified commit count shown by GitHub tree page: `98`  
Execution verdict: no implementation, no code, no approval of hardening execution.

---

## 0. HTTP Git Verification

| Check | Result | Evidence observed | Verdict |
|---|---:|---|---|
| exact tree URL | Opened | GitHub exact tree page opened at `SoulsLike2313/Imperium-` and displayed abbreviated commit `9319409`; root page displayed `98 Commits`. | PASS |
| primary matrix file | Opened | `ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/PREFILL_RU_OWNER_READABLE/FULL_QUESTIONNAIRE_PREFILL_MATRIX_RU_OWNER_APPROVED_V0_1.md` opened and showed full commit hash `931940980288cd42ece295d1107633d1fc55abf2`; GitHub rendered it as `380 lines (303 loc) · 30.9 KB`. | PASS |
| commit hash match | Matched | Primary file page showed `931940980288cd42ece295d1107633d1fc55abf2`; exact tree URL showed commit prefix `9319409`, matching the supplied HEAD prefix. | PASS |
| required files read | Read | Primary matrix file was read. Supporting package directory, dashboard doctrine, decision matrix, Sanctum integration draft, Kiro advisory buffer README/extract/manifest, and Doctrinarium README/status/contract/self-report were also read where accessible through exact SHA paths. | PASS |
| stop condition | Not triggered | No 404, access denied, wrong commit, or unreadable primary matrix condition occurred. | CONTINUE_REVIEW |

Files actually used as evidence:

| Path | Verification use |
|---|---|
| `ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/PREFILL_RU_OWNER_READABLE/FULL_QUESTIONNAIRE_PREFILL_MATRIX_RU_OWNER_APPROVED_V0_1.md` | Main Owner-readable V1 matrix. |
| `ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/README.md` | Package status: draft from Owner answers, not final hardening execution. |
| `ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/FOUNDATIONAL_ORGANS_V1_DECISION_MATRIX.md` | Compact decision list for ownership, evidence, dashboards, language, hardening target. |
| `ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/DASHBOARD_TRUTH_AND_BEAUTY_DOCTRINE_V0_1.md` | Dashboard truth/action/script/no-fake-green rules. |
| `ORGANS/ASTRONOMICON/TASK_DRAFTS/TASK-20260515-FOUNDATIONAL-ORGANS-V1-DEFINITION-V0_1/SANCTUM_INFINITY_GAUNTLET_INTEGRATION_DRAFT.md` | Sanctum aggregation model and action safety rule. |
| `ORGANS/ASTRONOMICON/ADVISORY_BUFFER/KIRO/FOUNDATIONAL_ORGANS_V1_QUESTIONNAIRE_20260515/README.md` | Kiro advisory boundary: reference only, not canon. |
| `ORGANS/ASTRONOMICON/ADVISORY_BUFFER/KIRO/FOUNDATIONAL_ORGANS_V1_QUESTIONNAIRE_20260515/EXTRACTED/questionnaire_extract.md` | Kiro extracted themes: role boundaries, evidence, dashboards, Owner-derived plan. |
| `ORGANS/ASTRONOMICON/ADVISORY_BUFFER/KIRO/FOUNDATIONAL_ORGANS_V1_QUESTIONNAIRE_20260515/MANIFEST/raw_file_manifest.json` | Advisory manifest: raw preserved, advisory not canon, Owner review required before canon. |
| `ORGANS/DOCTRINARIUM/README.md` | Doctrinarium v0.1 scope: law consistency, organ health gate, task-start gate, disabled Inquisition hook. |
| `ORGANS/DOCTRINARIUM/ORGAN_STATUS.json` | Current status still contains `canon_for_real_task_execution=false`, `owner_review_required=true`, and blockers. |
| `ORGANS/DOCTRINARIUM/ORGAN_CONTRACT.json` | Doctrinarium authority/not-authority, no-fake-green rules, evidence files, known blockers. |
| `ORGANS/DOCTRINARIUM/ORGAN_SELF_REPORT.json` | Stale self-report evidence: generated at older Git head, known blockers remain. |

---

## 1. Executive Verdict

`READY_FOR_STAGE_DECOMPOSITION: NO, NOT YET.`  
`READY_FOR_HARDENING_EXECUTION: NO.`  
`BLOCKERS: YES.`  
`NEXT BEST ACTION: create a reconciliation-and-gates package before generating executable Local Tasks/Stages.`

The matrix is good enough to become a decision input. It is not enough to launch the large multi-stage hardening execution.

The biggest failure risk is not missing ambition. The biggest failure risk is uncontrolled overlap: multiple organs want to talk about tasks, status, evidence, dashboards, gates, scripts, and receipts, but the execution authority lines are not yet machine-enforced.

Hardening execution must be blocked until these are created:

1. A machine-readable V1 ownership boundary contract.
2. A cross-organ evidence and receipt schema set.
3. A task corridor gate contract.
4. A dashboard truth contract with disabled-action semantics.
5. A Git/source-package integrity gate.
6. A stale-data model with hard dashboard behavior.
7. A repo-purity gate for `E:\IMPERIUM` versus `E:\IMPERIUM_CONTEXT`.
8. A decomposition budget that prevents both 40-stage chaos and one impossible mega-stage.

The Owner-readable RU matrix must remain Owner-facing companion material, not the canonical machine source. Canonical machine files must be English/UTF-8 and schema-validated.

---

## 2. What Is Strong

No praise padding. These are concrete strengths that reduce implementation risk if they are enforced.

| Strength | Evidence path | Why it matters | Required hardening action |
|---|---|---|---|
| Organ roles are mostly separated at intent level. | `FULL_QUESTIONNAIRE_PREFILL_MATRIX_RU_OWNER_APPROVED_V0_1.md`, sections for Astronomicon, Administratum, Officio Agentis, Doctrinarium. | The plan says Astronomicon owns task/stage topology, Administratum owns execution lifecycle truth, Officio owns role/mode contracts, Doctrinarium owns law/canon/readiness gates. | Convert this into `FOUNDATIONAL_ORGANS_V1_OWNERSHIP_MATRIX.json` and gate all V1 tasks against it. |
| No-fake-green is explicit. | `DASHBOARD_TRUTH_AND_BEAUTY_DOCTRINE_V0_1.md`; matrix `CROSS-07`. | It forbids green status without evidence, freshness, schema validity, provenance, and links. | Create `NO_FAKE_GREEN_DASHBOARD_GATE_V0_1.py` or equivalent checker before UI work. |
| Dashboard button/action contracts are recognized. | `DASHBOARD_TRUTH_AND_BEAUTY_DOCTRINE_V0_1.md`; matrix dashboard sections. | Buttons are a major false-success attack surface. | Require `dashboard_actions.json` with `enabled`, `disabled_reason`, `receipt_path`, `confirmation_required`, and `timeout`. |
| Kiro material is correctly isolated as advisory. | `ORGANS/ASTRONOMICON/ADVISORY_BUFFER/KIRO/.../README.md`; `MANIFEST/raw_file_manifest.json`. | Prevents external advisory from silently becoming canon. | Preserve this separation. Add an advisory-ingest receipt and `advisory_to_decision_trace.json`. |
| Doctrinarium status already admits non-green blockers. | `ORGANS/DOCTRINARIUM/ORGAN_STATUS.json`; `ORGAN_CONTRACT.json`; `ORGAN_SELF_REPORT.json`. | This prevents a false claim that Doctrinarium is fully operational. | V1 gate must fail hard if Doctrinarium claims task-start authority without current evidence. |
| Sanctum is described as aggregator, not backend replacement. | `SANCTUM_INFINITY_GAUNTLET_INTEGRATION_DRAFT.md`. | Prevents central UI from becoming source of truth. | Add `SANCTUM_READ_ONLY_AGGREGATION_CONTRACT_V0_1.json` before Sanctum action work. |
| Canonical files English / UI bilingual is stated. | Matrix `CROSS-08`; decision matrix `V1-DEC-012`. | Avoids language pollution in machine state and prevents mojibake. | Add i18n resource rule and UTF-8 checker to every stage touching UI or Owner-facing files. |

---

## 3. Blockers Before Hardening Execution

| Blocker ID | Blocker | Why it blocks | Concrete fix | Evidence path / missing artifact |
|---|---|---|---|---|
| B-01 | No machine-readable ownership boundary contract for the four organs. | The matrix states roles, but execution can still cross wires. | Create `ORGANS/ASTRONOMICON/TASK_DRAFTS/.../RECONCILIATION/FOUNDATIONAL_ORGANS_V1_OWNERSHIP_MATRIX.json` with `owns`, `may_read`, `may_write`, `must_not_decide`, `source_of_truth_for`, `dashboard_port`. | Matrix role sections; decision matrix `V1-DEC-001..003`, `V1-DEC-009..010`. |
| B-02 | Evidence/receipt schemas are named but not finalized. | Hardening can create incompatible receipts per organ. | Create `schemas/evidence_common_v0_1.schema.json`, `schemas/receipt_common_v0_1.schema.json`, `schemas/stage_receipt_v0_1.schema.json`, `schemas/action_receipt_v0_1.schema.json`. | Matrix `CROSS-01`, `CROSS-02`, `CROSS-11`, `CROSS-12`; decision matrix `V1-DEC-004..005`. |
| B-03 | Doctrinarium is not canon-green for real task execution. | Doctrinarium status has `canon_for_real_task_execution=false`, `owner_review_required=true`, and blockers. | Before hardening execution, require `DOCTRINARIUM_TASK_START_GATE_REPORT.json` with current Git HEAD and explicit `allowed_for_v1_hardening_planning` vs `allowed_for_execution`. | `ORGANS/DOCTRINARIUM/ORGAN_STATUS.json`. |
| B-04 | Stale self-report risk is real. | `ORGAN_SELF_REPORT.json` was generated at an older Git head, not HEAD `9319409...`. | Add stale gate: any organ self-report must include `git_head`, `created_at_utc`, `expires_after_seconds`, and `stale_status`; dashboard must show stale as amber/red, never green. | `ORGANS/DOCTRINARIUM/ORGAN_SELF_REPORT.json`; matrix `CROSS-02`, `CROSS-07`. |
| B-05 | Repo purity is an operational rule but not verified as a read artifact in the reviewed matrix. | Large hardening can dump runtime/outbox/bundles/private context into repo. | Add `REPO_PURITY_CONTRACT_V0_1.md/json` and checker `repo_purity_check` with allowed/disallowed roots. | Owner-supplied operational rule; not seen as a committed contract in the reviewed files. |
| B-06 | Dashboard action semantics are not yet enforceable. | A button can exist, look active, do nothing, and still show success. | Require `dashboard_actions.json` schema and checker before any dashboard V1 stage. | `DASHBOARD_TRUTH_AND_BEAUTY_DOCTRINE_V0_1.md`; `SANCTUM_INFINITY_GAUNTLET_INTEGRATION_DRAFT.md`. |
| B-07 | Stage decomposition budget is undefined. | The plan can turn into 40-stage chaos or one impossible task. | Define decomposition limits: General Task -> 6-10 Local Tasks; each Local Task -> 3-7 stages; any stage touching more than one source-of-truth boundary must split. | Matrix section 8 only says Local Tasks likely groups and stages are not final. |
| B-08 | Source-package integrity gate is missing. | Hardening may start from a stale matrix, advisory file, or altered draft. | Create `FOUNDATIONAL_ORGANS_V1_SOURCE_PACKAGE_MANIFEST.json` with SHA-256 for matrix, Kiro extract/manifest, Speculum review, Kiro recommendation, reconciliation output. | Kiro manifest exists for raw Kiro files; no equivalent source package manifest for the final hardening package. |
| B-09 | Inquisition hook is disabled but can be misread as active. | Future audit wording can fake security coverage. | Every Inquisition reference in V1 must carry `disabled_in_v1=true`, `not_a_gate=true`, and `future_hook_only`. | Doctrinarium README states disabled Inquisition hook; matrix references future Inquisition. |
| B-10 | Owner gates are doctrinal but not yet represented as machine gate objects. | Assistants can claim Owner intent without a receipt. | Define `OWNER_GATE_RECEIPT_V0_1` and require it for canon acceptance, dashboard dangerous actions, override, and hardening execution launch. | Matrix `DOCTR-04`, dashboard action doctrine, Owner V1 intent. |

Hard block: do not start implementation hardening until B-01, B-02, B-05, B-06, B-07, and B-08 are created at least as draft machine-readable contracts and accepted by Owner or Logos-Prime as execution preconditions.

---

## 4. Ownership Collision Attacks

| Collision | Risk | Failure mode | Blocks V1? | Precise fix |
|---|---|---|---:|---|
| Astronomicon vs Administratum | Both can appear to own task state. | Astronomicon stage map displays `active/completed` from its own file while Administratum ledger says different state. | YES | Add `source_of_truth_for.execution_state = ADMINISTRATUM`; Astronomicon may store `planned_stage_topology` and `display_state_cache` only with `source_admin_report_path`. |
| Astronomicon vs Administratum | Registration workflow overlaps with work packet creation. | Task is registered in Astronomicon but no Administratum `work_packet` exists; dashboard shows executable task. | YES | Split registration kinds: `TASK_MAP_REGISTERED` by Astronomicon; `EXECUTION_PACKET_OPENED` by Administratum. Execution starts only after both and a route sheet receipt exist. |
| Astronomicon vs Administratum | Stage transitions can be confused with stage completion. | Astronomicon marks next stage because graph says next, but Admin never validated evidence. | YES | Stage topology transition proposal must differ from `stage_completed`. Completion requires `ADMIN_STAGE_COMPLETION_RECEIPT`. |
| Administratum vs Doctrinarium | Admin wants task-start confirmation; Doctrinarium owns readiness gate. | Admin starts work because packet is valid even though law/organ health gate failed. | YES | `ADMIN_TASK_START_CONFIRMATION` must include `doctrinarium_gate_report_sha256` and `verdict=PASS|PASS_WITH_WARNINGS_ALLOWED_BY_OWNER`. |
| Administratum vs Doctrinarium | Admin owns Git truth operationally; Doctrinarium owns policy. | Git truth checker may pass while policy/law gate fails, but dashboard shows green. | YES | Separate fields: `git_truth_status` and `doctrine_gate_status`; top-level task-start verdict is min severity of both. |
| Officio Agentis vs Administratum | Role contract validation overlaps assignment/execution routing. | Admin assigns a Servitor without Officio contract; Officio later reports role invalid. | YES | Admin route sheet must include `officio_contract_id`, `contract_hash`, `allowed_actions`, and `stop_conditions`. |
| Officio Agentis vs Administratum | Officio may track availability/workload; Admin may track assigned role. | One says agent available, another says busy; task dispatched incorrectly. | NOT IF BOUNDED | V1 Officio only validates role contract and may expose advisory availability. Admin owns current assignment truth. |
| Officio Agentis vs Doctrinarium | Role contract laws can be split across role and doctrine files. | Officio permits an action that Doctrinarium law forbids. | YES | Officio contract validation must import `doctrinarium_law_index_hash` and fail on missing/unknown law references. |
| Officio Agentis vs Doctrinarium | Response contracts can become de facto law. | Officio response template overrides Owner doctrine. | YES | Response contract must include `doctrine_references`; Doctrinarium remains authority for hard laws. |
| Doctrinarium vs future Inquisition | Inquisition hook can be mistaken for active audit. | Dashboard shows audit-like badge from disabled hook. | YES | Disabled hook schema must expose `status=DISABLED_V1`, `no_audit_claim=true`, `display_badge=disabled`. |
| Sanctum vs organ dashboards | Sanctum can become source of truth by aggregation. | Sanctum normalizes or mutates organ status and hides organ blockers. | YES | Sanctum must be read-through: store only `source_path`, `source_hash`, `rendered_at_utc`, `stale_status`, never canonical organ state. |
| Sanctum vs organ dashboards | Too much data collapses readability. | Operator sees a beautiful cockpit but misses blocker details. | NO, IF LAYERED | Enforce four-level density: status, metrics, panels/actions, raw evidence; global blocker rail always visible. |
| Mechanicus/scripts/tools vs organ ownership | Scripts live outside organ folders but mutate organ state. | Mechanicus tool changes Admin/Astro files without ownership receipt. | YES | Every script must declare `owner_organ`, `allowed_write_roots`, `receipt_type`, `dry_run_supported`, `called_by_dashboard_allowed`. |
| Mechanicus/scripts/tools vs Doctrinarium | A generic validator can redefine law validation behavior. | Tool says PASS while Doctrinarium law checker would fail. | YES | Generic scripts can validate schema only; doctrinal verdict must come from Doctrinarium-owned checker/report. |

---

## 5. Missing Gates

| Gate | Required input | Required output | Pass condition | Stop condition | Evidence path to create |
|---|---|---|---|---|---|
| Git Truth Gate | Expected HEAD, commit count, exact tree URL, local HEAD if available. | `GIT_TRUTH_REPORT_V0_1.json`. | Exact HEAD matches; commit count matches; no floating branch dependency. | Wrong HEAD, 404 exact tree, stale local checkout, dirty repo. | `CURRENT_STATE/GIT_TRUTH_REPORT_V0_1.json` or `ORGANS/ADMINISTRATUM/REPORTS/...`. |
| Source Package Integrity Gate | Matrix, Kiro advisory/recommendation, Speculum report, reconciliation package hashes. | `FOUNDATIONAL_ORGANS_V1_SOURCE_PACKAGE_MANIFEST.json`. | Every source exists, hash recorded, status explicit. | Missing source, mismatched hash, advisory treated as canon. | `ORGANS/ASTRONOMICON/TASK_DRAFTS/.../RECONCILIATION/`. |
| Owner Decision Matrix Gate | Owner matrix and decisions. | `OWNER_DECISION_MATRIX_GATE_REPORT.json`. | All blocker decisions have accepted/deferred status; unresolved items are not execution inputs. | Any `needs_owner_review` required for execution remains unresolved. | `.../REPORTS/`. |
| Ownership Boundary Gate | Ownership matrix. | `OWNERSHIP_BOUNDARY_GATE_REPORT.json`. | Every state/evidence/action has exactly one owner organ. | More than one owner for execution state, role contracts, law verdict, task topology. | `.../RECONCILIATION/OWNERSHIP_BOUNDARY_GATE_REPORT.json`. |
| Stage Map Validity Gate | Proposed General/Local/Stage maps. | `STAGE_MAP_VALIDITY_REPORT.json`. | Stage IDs unique; dependencies resolvable; every stage has pass/fail, receipts, owner, rollback. | Missing pass/fail, cyclic dependency, too broad stage, no evidence. | `ORGANS/ASTRONOMICON/REPORTS/`. |
| Evidence Schema Gate | Evidence/receipt schema files. | `EVIDENCE_SCHEMA_GATE_REPORT.json`. | JSON validates; required fields present; unknown fields fail or warn per policy. | No schema; schema not applied; evidence file invalid. | `schemas/` and `ORGANS/ADMINISTRATUM/REPORTS/`. |
| No-Fake-Green Gate | Dashboard state + evidence references. | `NO_FAKE_GREEN_GATE_REPORT.json`. | Any green/PASS status has non-empty schema-valid fresh evidence and provenance. | Green with missing evidence, stale evidence, warnings hidden. | `ORGANS/DOCTRINARIUM/REPORTS/` or shared gate path. |
| Dashboard Truth Gate | `dashboard_state`, metrics, actions, scripts, i18n, style files. | `DASHBOARD_TRUTH_GATE_REPORT.json`. | All visible statuses/actions/scripts map to real backend artifacts or disabled reason. | Mock data in truth panel; button without receipt; script displayed but missing. | Per organ `DASHBOARD_DATA/REPORTS/`. |
| Task-Start Corridor Gate | TASK_ID, Admin packet, Astro map, Officio contract, Doctrinarium gate. | `TASK_START_CORRIDOR_GATE_REPORT.json`. | All four organs agree on TASK_ID, hashes, route sheet, role contract, laws. | Any organ mismatch, stale law, wrong role, missing route sheet. | `ORGANS/ADMINISTRATUM/REPORTS/`. |
| Rollback/Stop Gate | Stage scope and modified files. | `ROLLBACK_STOP_PLAN.json`. | Every stage has stop condition, rollback target, quarantine rule. | Stage can modify source without rollback/receipt. | Stage prompt package. |
| VM2/PC Boundary Gate | Execution target and sync policy. | `EXECUTION_BOUNDARY_REPORT.json`. | PC-only vs VM2 stages explicit; VM2 deferred if required. | Any task assumes VM2 when VM2 is offline/deferred. | `ORGANS/ADMINISTRATUM/ROUTES/`. |
| Registration Gate | General Task/Local Task/Stage Map. | `REGISTRATION_GATE_REPORT.json`. | Registration is local, typed, hash-backed, not execution approval. | Registration implies READY_FOR_AGENT or bypasses Owner. | `ORGANS/ASTRONOMICON/REGISTRY/...`. |
| UTF-8/Mojibake Gate | Touched text files. | `UTF8_REPORT.json`. | UTF-8 valid; no replacement characters; UI files have EN/RU separation. | Mojibake, BOM confusion where prohibited, Russian text in canonical machine keys. | `TOOLS/REPORTS/` or per-stage receipt. |
| Repo Purity Gate | Repo root and context root scans. | `REPO_PURITY_REPORT.json`. | Runtime/outbox/bundles/private context absent from repo; allowed files only. | `E:\IMPERIUM_CONTEXT` material committed into `E:\IMPERIUM`. | `ORGANS/ADMINISTRATUM/REPORTS/`. |

---

## 6. Fake-Green Attack Surface

| Attack scenario | Detection method | Required protection |
|---|---|---|
| Dashboard green without evidence. | Scan all `status=PASS/GREEN` fields and require `evidence_paths[]`, `source_report_path`, hash, freshness. | No-Fake-Green Gate; dashboard truth schema. |
| Stage completed without Administratum receipt. | For every completed stage, require `ADMIN_STAGE_COMPLETION_RECEIPT` linked to TASK_ID/STAGE_ID/RUN_ID. | Admin owns execution lifecycle; stage completion cannot be set by Astronomicon. |
| Task registered but not executable. | Separate `registered_for_planning`, `registered_for_execution`, `ready_for_agent`. | Astronomicon registration cannot imply Admin start confirmation. |
| Button present but not functional. | Validate `dashboard_actions.json`: every enabled action has target, confirmation, receipt, timeout, allowed role. | Disabled-by-default action policy. |
| Script present but not registered. | Validate `script_registry.json` or organ `SCRIPT_PORT`: path exists, owner, purpose, last run, verdict. | Script display contract. |
| Report exists but stale. | Require `generated_at_utc`, `git_head`, `expires_after_seconds`, `stale_status`. | Stale status model; stale cannot render as green. |
| JSON exists but invalid. | Schema validation in every gate. | Fail hard on invalid canonical JSON. |
| Warning hidden behind PASS. | Disallow `PASS` when warnings array non-empty; use `PASS_WITH_WARNINGS`; require warning count. | Universal status enum enforcement. |
| Disabled Inquisition hook pretending active. | Require disabled marker in hook state and dashboard rendering. | `INQUISITION_HOOK_DISABLED_V1` contract. |
| Sanctum aggregating stale organ states. | Sanctum aggregation report must compute worst freshness state and show source. | Sanctum read-only aggregation contract. |
| Advisory treated as canon. | Validate advisory folder status and canon receipt existence. | Doctrinarium advisory/canon gate. |
| Owner-readable RU matrix parsed as canonical machine law. | Check canonical source list: RU companion allowed only as human-facing evidence. | English canonical JSON decision package. |
| Agent claims correct role without Officio read receipt. | Require `OFFICIO_ROLE_CONTRACT_READ_RECEIPT` before stage prompt execution. | Officio contract gate. |
| GitHub floating branch shown instead of exact tree. | Gate requires exact SHA URL and local HEAD match. | Git truth gate. |

---

## 7. Dashboard Risk Review

| Risk | V1 requirement | Defer | Must be forbidden |
|---|---|---|---|
| Too much data in Sanctum. | Layered data density: global truth bar, organ status grid, selected workspace, evidence viewer. | Full graph exploration for all organs. | Single flat all-data page that hides blockers. |
| Performance below 60 FPS. | Use state-driven animation budget and reduce motion when data density rises. | Complex particle effects and heavy 3D. | Animation loop that blocks evidence loading or status updates. |
| Animations hiding truth. | Animation must communicate state: completed, active, future, blocked, waiting evidence. | Cosmetic-only animation. | Glowing green on stale/missing evidence. |
| Visual style fragmentation. | Organ-specific `dashboard_style.json` plus shared status vocabulary and typography rules. | Full design-system perfection. | Each organ inventing incompatible status colors/meaning. |
| Mock data leaking into production. | `mock_data=false` and `truth_source=backend_report` required for truth panels. | Demo-only playground outside truth panels. | Production truth panel reading fixtures or static demo JSON. |
| Buttons without receipts. | Every meaningful action has confirmation, command/action ID, expected report, expected receipt. | Bulk actions. | Any enabled action without receipt path and failure condition. |
| Bilingual UI polluting canonical data. | Canonical JSON keys/values English; UI labels in `dashboard_i18n/en.json` and `ru.json`. | Advanced localization workflow. | Russian labels embedded as canonical state values. |
| Unsafe side effects from dashboard actions. | Dashboard actions call organ-defined action contracts only. | Direct destructive actions. | Hidden shell execution from Sanctum or organ UI. |
| Dashboard becomes source of truth. | Dashboard reads backend reports and writes only action requests/receipts where allowed. | Dashboard-local state caches beyond render metadata. | Dashboard mutating canonical organ state directly. |
| Every script visible and working requirement overloads UI. | Show only registered scripts relevant to organ dashboard. | Full script browser across repo. | Unregistered script list with green status. |

V1 dashboard hard rule: a beautiful UI is allowed only as a reader/launcher with receipts. It cannot become the evidence source.

---

## 8. Task Corridor Red-Team

Target corridor:

`TASK_ID -> Doctrinarium -> Administratum -> Officio Agentis -> Astronomicon -> Administratum start confirmation -> stage execution -> Administratum records -> final bundle/continuity pack -> dashboards/Sanctum`

| Failure point | How the Servitor gets confused | Concrete guard |
|---|---|---|
| TASK_ID intake | Servitor brings a valid-looking TASK_ID from stale branch or old draft. | Git Truth Gate + Source Package Integrity Gate + `task_registry_head` field. |
| Doctrinarium gate | Servitor sees Doctrinarium folder and assumes canon readiness, while `ORGAN_STATUS.json` says owner review required and canon false. | Doctrinarium gate report must explicitly distinguish `planning_allowed` and `execution_allowed`. |
| Administratum lookup | Admin cannot find task in Astronomicon or finds old version. | Route sheet must include `astronomicon_task_path`, `task_hash`, `stage_map_hash`. |
| Officio contract | Wrong role contract is loaded or no response contract is enforced. | Stage prompt must include `officio_contract_id`, hash, required reads, stop conditions, response format. |
| Astronomicon stage map | Astronomicon has scope map but no execution truth. | Stage map stores topology only; progress fields must link to Admin receipts. |
| Admin start confirmation | Admin confirms route but does not include Doctrinarium/Officio proofs. | `TASK_START_CONFIRMATION_RECEIPT` must contain four-organ proof hashes. |
| Stage execution | Servitor updates files outside allowed scope or combines stage goals. | Stage prompt must include allowed paths, forbidden paths, receipt requirements, stop conditions. |
| Stage completion | Completion recorded from final message, not evidence. | Completion only after Admin validates receipt + evidence files + checks. |
| Final bundle | Bundle misses warnings, stale reports, or rollback notes. | Final bundle manifest must require warnings, blockers, checks, touched files, hashes, unresolved items. |
| Dashboards | Sanctum shows happy aggregate while one organ stale. | Aggregator status = worst-status across organ reports; stale overrides green. |

Specific mismatch risks:

| Mismatch | Required detection |
|---|---|
| Wrong TASK_ID passes | `TASK_ID` must appear consistently in Astro registry, Admin work packet, Officio stage prompt context, Doctrinarium gate report, all receipts. |
| Astronomicon/Admin disagree | Gate compares `stage_map_hash`, `current_stage`, `admin_lifecycle_state`, and `latest_stage_receipt`. |
| Officio validates wrong role | Contract hash and role ID must be included in stage prompt and receipt. |
| Doctrinarium allows stale laws | Gate report must include law index hash and generation HEAD. |
| Final bundle misses evidence | Bundle manifest schema must require per-stage receipt map and final unresolved warning list. |

---

## 9. Before-Work Checklist

### A. Must Do Before Execution

These are blockers. Do not start large hardening execution until they exist.

| # | Required item | Concrete artifact | Pass condition |
|---:|---|---|---|
| 1 | Reconciliation package | `RECONCILIATION/FOUNDATIONAL_ORGANS_V1_RECONCILED_PLAN.md` and `.json` | Owner matrix + Kiro recommendation + Speculum critique reconciled; conflicts listed. |
| 2 | Ownership boundary contract | `FOUNDATIONAL_ORGANS_V1_OWNERSHIP_MATRIX.json` | Every source-of-truth category has one owner. |
| 3 | Source package manifest | `FOUNDATIONAL_ORGANS_V1_SOURCE_PACKAGE_MANIFEST.json` | All input files hashed and exact SHA recorded. |
| 4 | Evidence/receipt schemas | `evidence_common`, `receipt_common`, `stage_receipt`, `action_receipt`, `gate_report` schemas | Sample files validate; invalid samples fail. |
| 5 | Gate list with stop conditions | `V1_HARDENING_GATE_INDEX.json` | Every gate has input, output, pass, stop, evidence path. |
| 6 | Repo purity contract | `REPO_PURITY_CONTRACT_V0_1.json` | `E:\IMPERIUM_CONTEXT` boundary enforced; no runtime/private context under repo. |
| 7 | Dashboard truth contract | `dashboard_state`, `dashboard_actions`, `dashboard_metrics`, `dashboard_i18n`, `dashboard_style` schemas | Enabled actions require receipts; mock data cannot feed truth panel. |
| 8 | Stale status model | `STALE_STATUS_MODEL_V0_1.json` | `generated_at`, `git_head`, `last_checked_at`, `expires_after`, `stale_status` required. |
| 9 | Doctrinarium current gate report | `DOCTRINARIUM_TASK_START_GATE_REPORT.json` | Explicit current HEAD; no full execution green if canon still false. |
| 10 | Decomposition budget | `V1_HARDENING_DECOMPOSITION_RULES.md/json` | Max layers and split rules defined. |
| 11 | Owner manual launch gate | `OWNER_HARDENING_EXECUTION_LAUNCH_RECEIPT.json` | Owner approves execution after gate reports, not before. |
| 12 | Stage prompt contract | `STAGE_PROMPT_CONTRACT_V0_1.md/json` | Every prompt includes scope, files, checks, receipts, stop conditions, no-go zones. |

### B. Should Do Before Execution

Strongly recommended. These reduce rework but do not necessarily block planning.

| # | Item | Concrete artifact | Reason |
|---:|---|---|---|
| 1 | Sample E2E dry-run with a dummy task | `DUMMY_TASK_CORRIDOR_DRY_RUN_REPORT.json` | Proves gates can connect before large task. |
| 2 | Dashboard fixture quarantine rule | `DASHBOARD_FIXTURE_POLICY.md` | Prevents mock data from leaking into truth panels. |
| 3 | Warning baseline | `WARNING_BASELINE_V0_1.json` | Prevents warning flood blindness. |
| 4 | Script registry index | `SCRIPT_REGISTRY_V0_1.json` | Prevents unowned scripts from being shown or launched. |
| 5 | Archive index stub | `ARCHIVE_INDEX_V0_1.json` | Supports 14-day retention without deleting evidence. |
| 6 | Minimal visual token file | `DASHBOARD_STATUS_VISUAL_TOKENS_V0_1.json` | Prevents conflicting green/amber/red semantics across organs. |
| 7 | Cross-organ import/export pack contract | `ORGAN_REVIEW_PACK_CONTRACT_V0_1.json` | Controls Speculum/Kiro/Owner pack flow. |
| 8 | UTF-8 touched-file report | `UTF8_TOUCHED_FILES_REPORT.json` | Prevents mojibake regression. |

### C. Can Defer

Do not overload first V1 hardening.

| Defer item | Defer target | Reason |
|---|---|---|
| Full Inquisition build | V1.1 / Mega-hardening | Hook must remain disabled in V1. |
| Autonomous agent assignment | Later Officio/Admin integration | Owner-gated/manual-first rule. |
| Full semantic law search | V1.1 | Basic keyword/path search is sufficient for V1. |
| Advanced visual side-by-side law diff | V1.1 | Timeline + Git history + receipt is enough for V1. |
| Heavy graph UI for all organs | Later | First prove truthful reports and stage topology. |
| Bulk dashboard actions | Later | Too risky before action receipts are hardened. |
| Scheduled Admin reports | V1.1 | On-demand reports first. |
| Full performance analytics | Later | Basic truth metrics first. |
| Cloud/shared service architecture | Not V1 | Local-first constraint. |

---

## 10. Stage Decomposition Warnings

Safe decomposition layers:

1. `General Task`: one V1 hardening mission.
2. `Local Tasks`: bounded components or corridors.
3. `Stages`: executable slices with receipts.
4. `Stage Prompts`: one Servitor-executable unit.

Do not add more layers for V1. Extra hierarchy will create tracking overhead without stronger evidence.

### Recommended Local Task groups

| Local Task group | Purpose | Split warning |
|---|---|---|
| Cross-organ contracts/schemas | Evidence, receipts, ownership, stale status, dashboard contracts. | Must come before organ-specific dashboard hardening. |
| Astronomicon V1 | Task memory, stage maps, registration workflow, review packs. | Must not record execution completion truth. |
| Administratum V1 | Work packets, lifecycle truth, route sheets, black-box ledger, final bundle. | Must not decide law/canon or role validity. |
| Officio Agentis V1 | Role/mode/agent contracts, response contracts, read receipts. | Must not assign agents autonomously in V1. |
| Doctrinarium V1 gate hardening | Law/canon, organ health, task-start gate, disabled Inquisition hook. | Must not claim full Inquisition audit. |
| Dashboard truth layer | Per-organ dashboard contracts and data readers. | Must not build beauty before truth contract. |
| Sanctum aggregation layer | Read-only central bridge. | Must not mutate organ canonical state. |
| E2E corridor proof | Dummy/controlled task across four organs. | Must not be the first stage; needs contracts first. |
| Certification/continuity pack | Final evidence bundle and unresolved risk list. | Must not erase warnings. |

### What a stage must never combine

| Forbidden combination | Reason |
|---|---|
| Schema definition + dashboard UI polish + execution mutation | Too broad; impossible to verify cleanly. |
| Astronomicon stage map writes + Administratum lifecycle completion writes | Source-of-truth collision. |
| Officio role contract creation + Doctrinarium law acceptance | Role rules are not canon acceptance. |
| Dashboard action implementation + button styling | Action safety must pass before beauty. |
| Inquisition hook + Doctrinarium enforcement | Hook disabled in V1; no fake audit. |
| Git truth checker + VM2 sync | VM2 is not required and can create route drift. |
| Evidence schema changes + mass migration | High rollback complexity. |

### Stop and ask Owner when

| Trigger | Required Owner question |
|---|---|
| A stage needs to change source-of-truth ownership. | “Do you approve moving this truth category from organ A to organ B?” |
| A dashboard action can mutate canonical state. | “Should this be enabled in V1 or disabled with reason?” |
| A checker produces PASS_WITH_WARNINGS for a hard gate. | “Can warnings be accepted for this launch gate?” |
| More than 10 Local Tasks or more than 60 total stages appear. | “Do we split into V1a/V1b?” |
| Any task needs VM2 while VM2 is deferred/offline. | “Do we re-enable VM2 or keep this PC-only?” |
| Any RU owner-readable document becomes machine-canonical. | “Do we create English canonical counterpart first?” |

### Decomposition budget

| Limit | Value |
|---|---:|
| General Task count | 1 |
| Local Task target | 7-9 |
| Local Task hard maximum before split | 12 |
| Stage target per Local Task | 3-6 |
| Stage hard maximum per Local Task | 8 |
| Total stages before mandatory replan | 45 |
| Files touched per stage target | 1-5 |
| Owner gate after every Local Task | Required |

### Stage prompt requirements

Each stage prompt must contain:

- exact Git HEAD expected;
- local task ID and stage ID;
- allowed files and forbidden files;
- source-of-truth owner organ;
- inputs with hashes where practical;
- exact outputs;
- required checks;
- required receipts;
- pass/fail conditions;
- rollback/quarantine instructions;
- no READY_FOR_AGENT escalation unless explicitly part of later Owner-approved task;
- no VM2 unless a route gate says VM2 is active;
- no Inquisition activation;
- no fake green.

---

## 11. Evidence / Receipt Architecture Gaps

Current idea reviewed:

- JSON canonical evidence.
- Optional Markdown summaries.
- 14-day routine archive threshold.
- Canonical receipts/history not casually deleted.
- Action receipts.
- Law change receipts.
- Stage receipts.
- Final bundle.

This is directionally usable. It is not complete enough for V1 execution.

### Missing evidence types

| Evidence type | Owner organ | Why needed | Schema/file to create |
|---|---|---|---|
| `gate_report` | Gate owner or shared | Every gate needs pass/stop proof. | `schemas/gate_report_v0_1.schema.json` |
| `source_package_manifest` | Astronomicon/Admin shared | Proves hardening input set. | `FOUNDATIONAL_ORGANS_V1_SOURCE_PACKAGE_MANIFEST.json` |
| `ownership_boundary_report` | Doctrinarium/Administratum shared | Prevents organ collision. | `OWNERSHIP_BOUNDARY_GATE_REPORT.json` |
| `task_start_confirmation_receipt` | Administratum | Proves four-organ corridor readiness. | `admin_task_start_confirmation_receipt_v0_1.schema.json` |
| `role_contract_read_receipt` | Officio Agentis | Proves agent read correct contract. | `officio_role_contract_read_receipt_v0_1.schema.json` |
| `law_gate_receipt` | Doctrinarium | Proves laws checked at current HEAD. | `doctrinarium_law_gate_receipt_v0_1.schema.json` |
| `stage_topology_receipt` | Astronomicon | Proves stage map registered/changed. | `astronomicon_stage_topology_receipt_v0_1.schema.json` |
| `admin_stage_completion_receipt` | Administratum | Proves stage completion truth. | `admin_stage_completion_receipt_v0_1.schema.json` |
| `dashboard_action_receipt` | Action owner organ | Proves UI action did what it claims. | `dashboard_action_receipt_v0_1.schema.json` |
| `dashboard_render_report` | Dashboard owner | Proves UI rendered real data and freshness. | `dashboard_render_report_v0_1.schema.json` |
| `stale_state_report` | Each organ/Sanctum | Prevents stale green. | `stale_state_report_v0_1.schema.json` |
| `repo_purity_report` | Administratum/Mechanicus | Prevents context pollution. | `repo_purity_report_v0_1.schema.json` |
| `final_bundle_manifest` | Administratum | Proves final evidence completeness. | `final_bundle_manifest_v0_1.schema.json` |

### Prevent evidence rot

| Rot vector | Protection |
|---|---|
| Evidence path moves | Store `path`, `sha256`, `created_at_utc`, `git_head`, `logical_id`, and archive index pointer. |
| Evidence becomes stale | Store `expires_after_seconds` and `stale_status`; dashboard must compute freshness. |
| Receipt unreadable by humans | Optional MD summary allowed, but JSON remains canonical. |
| Warnings disappear | Receipt schema requires `warnings_array`, even if empty; PASS_WITH_WARNINGS requires non-empty warnings. |
| Archive breaks links | Archive index must preserve old path, new path, hash, reason, moved_at_utc. |
| External advisory treated as law | Advisory manifest and Doctrinarium canon receipt must be separate. |

### Administratum vs Doctrinarium evidence ownership

| Evidence category | Owner |
|---|---|
| Execution lifecycle, stage completed, work packet, route sheet, final bundle | Administratum |
| Law/canon state, law change receipt, readiness gate, violation report | Doctrinarium |
| Task scope, stage topology, registration pack, review/export/import pack | Astronomicon |
| Role/mode/response contract, read receipt, role compliance proof | Officio Agentis |
| Shared schema definitions | Registry/shared schema zone, with owner field and Doctrinarium policy review |
| Script run reports | Script owner organ or Mechanicus, but effect receipt belongs to the mutated organ |

### How Sanctum should link evidence

Sanctum must store/render only:

- source organ ID;
- source report path;
- source report hash;
- source generated time;
- rendered time;
- stale status;
- top-level status;
- warnings/blockers summary;
- evidence links.

Sanctum must not store canonical execution state, law verdicts, role contract verdicts, or stage topology as its own truth.

---

## 12. Kiro Recommendation Prompt Guidance

Kiro should be asked for practical recommendations only, bounded to the current Git reality and Owner matrix.

### Ask Kiro to focus on

| Focus | Specific ask |
|---|---|
| Minimal implementation path | “Given the Owner V1 matrix, what is the smallest safe implementation order?” |
| Schema set | “Which 6-10 schemas must exist before execution, and which can wait?” |
| Gate design | “Propose lightweight gate reports for Git truth, evidence, dashboard truth, task-start corridor, stale state, repo purity.” |
| Dashboard truth architecture | “How should dashboards read backend reports without becoming source of truth?” |
| Sanctum data density | “How to aggregate multiple organ dashboards without flooding UI or hiding blockers?” |
| Stage grouping | “Suggest Local Task and stage grouping with a max stage budget.” |
| Fake-green prevention | “List concrete failure cases and checks, not abstract best practices.” |
| Performance | “How to maintain readable dashboard performance with animation budget and large state payloads?” |
| Simplicity | “What can be plain files and scripts now instead of frameworks?” |
| Deferral | “What to defer to V1.1 to avoid overloading V1?” |

### Kiro must not be allowed to do

| Forbidden Kiro direction | Reason |
|---|---|
| Turn advisory into canon. | Owner and Doctrinarium own canon acceptance. |
| Recommend cloud-first architecture. | IMPERIUM is local-first. |
| Replace Owner gate with automation. | Manual Owner gate is mandatory. |
| Collapse organ ownership into one service. | Breaks organ source-of-truth boundaries. |
| Propose full Inquisition activation for V1. | Inquisition hook is disabled in V1. |
| Push heavy dependency frameworks as mandatory. | Current project needs contracts/checkers first. |
| Produce huge abstract architecture without files/gates. | Not actionable. |
| Make Sanctum the backend source of truth. | Sanctum must aggregate. |
| Recommend autonomous agent assignment in V1. | Owner-gated and Officio/Admin split not hardened yet. |
| Ignore Git HEAD and source package hashes. | Stale Git truth is a known failure mode. |

### Kiro prompt must include these constraints

- Exact HEAD: `931940980288cd42ece295d1107633d1fc55abf2`.
- Matrix path and status: Owner-readable approved draft, not final law/execution package.
- Kiro advisory status: reference only until Owner/Doctrinarium process.
- V1 target: complete logged task corridor, not full mega-hardening.
- Do not implement, commit, or push.
- Return concrete artifacts: files, schemas, gates, scripts, receipts, stage split.

---

## 13. Recommended Corrections to the Matrix

These are not implementation changes. They are corrections needed before the matrix can feed hardening execution.

| Matrix area | Problem | Correction |
|---|---|---|
| Global status | `accepted_draft` can be mistaken for execution approval. | Add `execution_authorized=false` and `requires_reconciliation=true`. |
| Cross-organ standards | Evidence fields are listed but no schema priority exists. | Add “V1 schema minimum set” row with required first schemas. |
| Ownership enforcement | Good intent, insufficient machine mapping. | Add explicit source-of-truth matrix: task topology, execution lifecycle, role contract, law verdict, dashboard render, action receipt, final bundle. |
| Lifecycle hooks | Hooks are named, but owner per hook is not fixed. | Add `hook_owner_organ` and `receipt_required` per hook. |
| Dashboard language | EN/RU rule exists, but not enough to prevent canonical pollution. | Add `canonical_state_language=ENGLISH_ONLY`; UI labels only in i18n resources. |
| Astronomicon | “registration workflow” can imply execution registration. | Split `planning_registration`, `stage_map_registration`, and `execution_packet_opened_by_admin`. |
| Astronomicon dashboard | Buttons for registration/download/upload/export are desired. | Add disabled-by-default requirement until action contract + receipts exist. |
| Administratum | Execution black box role is correct but broad. | Add exact V1 ledgers: `work_packet`, `stage_ledger`, `route_sheet`, `bundle_manifest`, `continuity_pack`. |
| Administratum priority | Priority/order warning is accepted, but scheduler boundary needs machine terms. | Add `no_autonomous_scheduler_v1=true`; dependency violation may block, priority alone may not auto-reorder. |
| Officio Agentis | Role liveness proof is useful but can become assignment authority. | Add `assignment_truth_owner=ADMINISTRATUM`, `contract_validity_owner=OFFICIO_AGENTIS`. |
| Officio dashboard | Registration forms may be disabled/Owner-gated. | Add exact disabled action display rule: visible disabled action must show `disabled_reason` and `required_gate`. |
| Doctrinarium | Task-start gate depends on incomplete canon state. | Add gate modes: `planning_gate`, `execution_gate`, `canon_acceptance_gate`; do not conflate. |
| Doctrinarium/Inquisition | Disabled Inquisition hook needs stronger display language. | Add `INQUISITION_V1_STATUS=DISABLED_FUTURE_HOOK_NOT_AUDIT`. |
| Evidence retention | 14-day threshold is useful but vague. | Add archive index requirement and list “never delete casually” categories. |
| Dashboard animation | Owner wants high beauty; risk of hiding truth. | Add “truth precedence”: status labels, blocker reasons, evidence links must remain visible even when animations fail/disabled. |
| Stage interpretation | Local task groups are listed but not gated. | Add decomposition budget and split rules before stage generation. |
| Advisory/review pipeline | Good pipeline but missing source package manifest. | Add source manifest step before reconciliation and final General Task. |
| Repo purity | Not visible in reviewed matrix as a committed rule. | Add repo purity row: runtime/outbox/bundles/private context outside repo; checker required. |
| VM2 | VM2 deferred/offline from current operational context, not in matrix. | Add execution environment row: PC-only unless route gate says VM2 active. |
| READY_FOR_AGENT | Must remain false until late gate. | Add `READY_FOR_AGENT` escalation conditions; hard block in early hardening stages. |

---

## 14. Final Verdict

- `READY_FOR_STAGE_DECOMPOSITION: NO`
- `READY_FOR_HARDENING_EXECUTION: NO`
- `BLOCKERS: YES`
- `NEXT BEST ACTION: Build and review the reconciliation/gate package, then generate the hardening General Task.`

### Top 10 fixes before execution

1. Create `FOUNDATIONAL_ORGANS_V1_OWNERSHIP_MATRIX.json`.
2. Create `FOUNDATIONAL_ORGANS_V1_SOURCE_PACKAGE_MANIFEST.json`.
3. Create minimal common evidence/receipt schemas.
4. Create `V1_HARDENING_GATE_INDEX.json` with stop conditions.
5. Create dashboard truth/action schemas.
6. Create stale status model and no-stale-green checker requirement.
7. Create repo purity contract and checker requirement.
8. Produce current Doctrinarium gate report at HEAD `931940980288cd42ece295d1107633d1fc55abf2`.
9. Define decomposition budget before Local Task/Stage generation.
10. Require Owner launch receipt before any hardening execution.

### Top 10 risks during execution

1. Astronomicon and Administratum both writing execution state.
2. Doctrinarium treated as full canon gate while current status still blocks real execution.
3. Dashboard showing green from stale or mock data.
4. Button/action UI created before action receipts exist.
5. Kiro advisory recommendations accidentally promoted to canon.
6. RU Owner-readable matrix used as canonical machine state.
7. Stage plan explodes past manageable size.
8. Scripts mutate organ files without ownership metadata.
9. Repo polluted with runtime/outbox/bundle/private context artifacts.
10. Sanctum becomes a source of truth instead of a read-through aggregation shell.

### Recommended next step

Create one small planning task, not implementation:

`TASK-20260515-FOUNDATIONAL-ORGANS-V1-RECONCILIATION-GATES-V0_1`

Purpose:

- reconcile Owner matrix + Kiro advisory/recommendations + Speculum critique;
- produce ownership matrix;
- produce gate index;
- produce source package manifest;
- define minimum schemas and decomposition budget;
- keep READY_FOR_AGENT false;
- keep VM2 out;
- do not implement dashboards or organs yet.

Expected verdict after that task:

`READY_FOR_STAGE_DECOMPOSITION: CONDITIONAL_YES_FOR_PLANNING_ONLY`  
`READY_FOR_HARDENING_EXECUTION: STILL_NO_UNTIL_OWNER_LAUNCH_GATE`

Hard stop language:

Do not build Sanctum buttons before dashboard action contracts and receipts exist.  
Do not let Astronomicon mark execution progress without Administratum receipts.  
Do not let Administratum start work without Doctrinarium and Officio proof hashes.  
Do not treat Doctrinarium v0.1 as fully canon-green while its own status says owner review and hard-law blockers remain.  
Do not treat Kiro advisory as law.  
Do not let dashboards show green from stale reports, mock data, or missing evidence.  
Do not launch the big hardening task until the reconciliation/gate package exists.
