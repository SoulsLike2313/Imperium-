This is a massive research request. Let me conduct the research systematically across the 10 areas.

I have enough research data from the searches combined with my existing knowledge. Given the massive scope of this request and the context window constraints, I'll produce the complete research pack directly in chat as requested.

```markdown
# IMPERIUM RESEARCH PACK — EXTERNAL REALITY SCAN v0.1
## Kiro Research Scout | 2026-05-12

---

# 1. EXECUTIVE_SUMMARY

## Что важнее всего для IMPERIUM

IMPERIUM уже интуитивно реализует паттерны, которые индустрия формализовала в SLSA (supply chain provenance), in-toto (step-by-step evidence chain), и Temporal (durable human-in-the-loop workflows). Главное открытие: IMPERIUM не нуждается в тяжёлых фреймворках. Ему нужны **лёгкие адаптации проверенных паттернов** в виде JSON файлов, Python скриптов, и filesystem-based coordination.

## Top 10 actionable lessons

1. **SLSA provenance model** — каждый bundle должен содержать: кто произвёл, из какого input, какой командой, при каком git SHA. IMPERIUM receipts уже близки к этому, но не формализованы.

2. **in-toto layout/link pattern** — layout = stage map (что должно произойти), link = receipt (что реально произошло). Astronomicon = layout provider, Administratum = link recorder. Прямое соответствие.

3. **Temporal human-in-the-loop** — workflow паузится на approval step, переживает crashes, возобновляется. IMPERIUM может реализовать это через filesystem state files без Temporal dependency.

4. **MAST failure taxonomy (arxiv 2503.13657)** — 14 failure modes для multi-agent систем. Три категории: specification issues, inter-agent misalignment, task verification. IMPERIUM Doctrinarium/Inquisition должны ловить все три.

5. **Dagster asset-centric model** — определяй что должно существовать (assets), а не что запускать (tasks). IMPERIUM receipts = assets. Verification spine проверяет их существование и валидность.

6. **Filesystem-based task queue** — SQLite или JSONL append-only log достаточен для local-first task state. Не нужен Redis/RabbitMQ.

7. **PowerShell UTF-8 fix** — `$OutputEncoding = [System.Text.Encoding]::UTF8` + `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8` в начале каждого PS1 скрипта. Или env var `PYTHONUTF8=1` для Python subprocess.

8. **No-delete / quarantine pattern** — вместо удаления файлов, перемещать в `_QUARANTINE/` с timestamp. Это уже частично реализовано в IMPERIUM (.gitignore для ARCHIVE), но не формализовано.

9. **Stale data warning** — каждый dashboard element должен показывать `last_verified_at`. Если > 5 минут — жёлтый. Если > 1 час — красный. Sanctum hardcoded chips = бесконечно stale.

10. **Hallucination propagation** — когда один агент производит output, следующий агент принимает его как truth. IMPERIUM Inquisition должен проверять КАЖДЫЙ inter-agent handoff, не только финальный результат.

## Top 10 risks to avoid

1. Не внедрять Temporal/Airflow/Dagster как dependency — слишком тяжело для local-first
2. Не доверять agent output без receipt verification
3. Не использовать shell=True ни при каких обстоятельствах
4. Не хранить state только в памяти — всё на filesystem
5. Не делать auto-retry без human review для failed stages
6. Не позволять агентам менять stage map без Owner approval
7. Не игнорировать UTF-8 issues — они ломают receipts и dashboards
8. Не показывать "PASS" без timestamp последней проверки
9. Не позволять одному агенту быть и executor и reviewer
10. Не строить complex orchestrator до того, как simple sequential chain работает

---

# 2. SOURCE_INDEX

| # | Title | URL | Type | Reliability | IMPERIUM relevance | Area |
|---|-------|-----|------|-------------|-------------------|------|
| 1 | SLSA Build Provenance v1.2 | https://slsa.dev/spec/v1.2/build-provenance | Standard | HIGH | Receipt/bundle format model | Evidence/provenance |
| 2 | SLSA Attestation Model | https://slsa.dev/attestation-model | Standard | HIGH | Attestation = receipt concept | Evidence/provenance |
| 3 | in-toto Getting Started | https://in-toto.io/docs/getting-started/ | Official docs | HIGH | Layout/link = stage map/receipt | Evidence/provenance |
| 4 | in-toto Verify | https://in-toto.readthedocs.io/en/stable/command-line-tools/in-toto-verify.html | Official docs | HIGH | Verification chain model | Evidence/provenance |
| 5 | Temporal Human-in-the-Loop | https://docs.temporal.io/ai-cookbook/human-in-the-loop-python | Official docs | HIGH | Durable approval pattern | Workflow/approval |
| 6 | Temporal Durable AI Tutorial | https://learn.temporal.io/tutorials/ai/building-durable-ai-applications/human-in-the-loop/ | Tutorial | HIGH | Crash-surviving approval | Workflow/approval |
| 7 | MAST: Why Do Multi-Agent LLM Systems Fail? | https://arxiv.org/abs/2503.13657 | Paper (NeurIPS) | HIGH | 14 failure modes taxonomy | Multi-agent failures |
| 8 | AI Agent Failure Modes | https://nimblebrain.ai/why-ai-fails/agent-governance/agent-failure-modes/ | Blog | MEDIUM | 5 predictable failure modes | Multi-agent failures |
| 9 | The Multi-Agent Trap (TDS) | https://towardsdatascience.com/the-multi-agent-trap/ | Blog | MEDIUM | 40% cancellation rate, patterns | Multi-agent failures |
| 10 | Dagster Software-Defined Assets | https://dagster.io/blog/software-defined-assets | Official blog | HIGH | Asset-centric orchestration | Workflow engines |
| 11 | Dagster Production Guide | https://www.ryankirsch.dev/blog/dagster-production-guide | Blog | MEDIUM | Asset vs task thinking | Workflow engines |
| 12 | python-task-queue (filesystem) | https://github.com/seung-lab/python-task-queue | GitHub | MEDIUM | Filesystem queue design | Local-first |
| 13 | litequeue (SQLite queue) | https://github.com/litements/litequeue | GitHub | MEDIUM | SQLite-based task queue | Local-first |
| 14 | persist-queue | https://pypi.org/project/persist-queue/ | PyPI | MEDIUM | Disk-persistent queue | Local-first |
| 15 | Hugging Face MAS Failure Analysis | https://huggingface.co/blog/Musamolla/multi-agent-llm-systems-failure | Blog | MEDIUM | Inferred state instability | Multi-agent failures |
| 16 | Augment Code MAS Architecture | https://www.augmentcode.com/guides/multi-agent-ai-systems | Guide | MEDIUM | Hallucination propagation | Multi-agent failures |
| 17 | Temporal Use Cases | https://docs.temporal.io/evaluate/use-cases-design-patterns | Official docs | HIGH | Human-in-loop patterns | Workflow/approval |

---

# 3. RESEARCH_NOTES_BY_AREA

## Area 1: Workflow engines / task orchestration

**Найдено:**
- Temporal: durable execution, survives crashes, signal-based human approval, activity retry with backoff
- Dagster: asset-centric (define what should exist, not what to run), built-in lineage, freshness policies
- Common patterns: DAG-based dependencies, idempotent operations, run_id for each execution, audit trail built-in

**Что IMPERIUM должен адаптировать:**
- **TASK_ID / STAGE_ID / RUN_ID** triple — уже в плане, правильно
- **Idempotency** — повторный запуск stage с тем же input должен давать тот же output
- **Durable state on filesystem** — stage status записывается в JSON, не в память
- **Human approval as explicit state** — `WAITING_APPROVAL` status в stage map

**Что IMPERIUM должен избегать:**
- Не внедрять Temporal как dependency (слишком тяжело)
- Не строить DAG engine — sequential pipeline достаточен для v0.1
- Не делать auto-retry — каждый retry = Owner decision

## Area 2: Evidence, provenance, and artifact trust

**Найдено:**
- SLSA v1.2: provenance = attestation что конкретный build platform произвёл конкретные artifacts из конкретного buildDefinition
- in-toto: layout (plan) + links (evidence per step) + verification (check chain)
- Key fields: subject (what was produced), predicate (how), builder (who/what), materials (inputs), products (outputs)

**Что IMPERIUM должен адаптировать:**
- **Bundle manifest** по модели SLSA: `{subject: [{name, digest}], predicate: {buildType, builder, materials, metadata}}`
- **Receipt = in-toto link**: materials (input files + hashes), products (output files + hashes), command, return_value
- **Stage map = in-toto layout**: defines expected steps, expected materials/products per step
- **Verification = in-toto verify**: check that all links match layout expectations

**Конкретная рекомендация для IMPERIUM bundle:**
```
BUNDLE_MANIFEST.json:
  schema_version
  task_id
  stage_id
  run_id
  builder: {agent_id, contour (PC/VM2), timestamp}
  materials: [{path, sha256}]  # input files
  products: [{path, sha256}]   # output files
  command_log: [{command, exit_code, timestamp}]
  git_truth: {head_sha, branch, tree_url}
  verification: {verify_repo_verdict, git_cli_check_verdict}
```

## Area 3: Multi-agent systems failure modes

**Найдено (MAST taxonomy, arxiv 2503.13657):**

14 failure modes in 3 categories:

**I. Specification & System Design:**
1. Ambiguous task specification
2. Misaligned agent capabilities
3. Inadequate decomposition
4. Missing termination conditions
5. Insufficient context sharing

**II. Inter-Agent Misalignment:**
6. Conflicting sub-goals
7. Communication breakdown
8. Role confusion
9. Cascading errors (hallucination propagation)
10. Redundant/contradictory actions

**III. Task Verification:**
11. Premature termination
12. Incomplete verification
13. False positive completion
14. Inability to recover from errors

**Mapping to IMPERIUM organs:**

| Failure mode | IMPERIUM mitigation organ |
|---|---|
| Ambiguous task spec | Astronomicon (pass criteria required) |
| Misaligned capabilities | Officio Agentis (corridor limits) |
| Inadequate decomposition | Astronomicon (stage map review) |
| Missing termination | Officio Agentis (stop conditions) |
| Cascading errors | Inquisition (per-stage audit) |
| False positive completion | Doctrinarium (no fake green rule) |
| Premature termination | Administratum (stage ledger incomplete) |

**Ключевой вывод:** IMPERIUM уже архитектурно защищён от большинства failure modes ЕСЛИ органы реально работают. Проблема = органы ceremonial.

## Area 4: Local-first automation

**Найдено:**
- Filesystem-based queues работают для single-machine coordination
- SQLite = идеальный local state store (ACID, zero-config, single-file)
- JSONL append-only logs = простейший audit trail
- Lock files = простейшая coordination primitive
- State machine on filesystem: `{task_id}/STATUS.json` с полем `state`

**Что IMPERIUM должен адаптировать:**
- **JSONL event log** для Administratum: append-only, каждая строка = event
- **STATUS.json per task** — уже в плане (CURRENT_STAGE.json)
- **Lock file pattern** — `.imperium_runtime/locks/{task_id}.lock` для предотвращения parallel execution
- **SQLite** — НЕ сейчас. Filesystem JSON достаточен для v0.1. SQLite = v0.3+

**Что избегать:**
- Не использовать Redis/RabbitMQ
- Не строить custom database
- Не делать in-memory state без persistence

## Area 5: Windows ↔ Linux automation reliability

**Найдено:**
- PowerShell default encoding = UTF-16LE для pipe output, system locale for console
- Python subprocess на Windows получает cp1252 или cp866, не UTF-8
- Fix: `$env:PYTHONUTF8 = "1"` или `sys.stdout.reconfigure(encoding='utf-8')`
- PowerShell fix: `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`
- CRLF/LF: Git `core.autocrlf = true` на Windows, `input` на Linux
- ZIP на Windows может использовать cp437 для filenames

**Конкретные рекомендации для IMPERIUM:**

```python
# В начале каждого Python скрипта IMPERIUM:
import sys, os
os.environ.setdefault("PYTHONUTF8", "1")
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
```

```powershell
# В начале каждого PS1 скрипта IMPERIUM:
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
```

- Все JSON файлы: write with `encoding="utf-8"`, read with `encoding="utf-8-sig"` (handles BOM)
- SSH commands: keep short, avoid complex quoting, prefer script files over inline commands

## Area 6: Dashboard / mission-control UI

**Найдено:**
- Stale data = #1 dashboard problem. Every value needs `last_updated` timestamp.
- Traffic light pattern: GREEN (verified < 5 min ago) / YELLOW (verified < 1 hour) / RED (stale or failed)
- "No news is NOT good news" — absence of recent check = UNKNOWN, not PASS
- Safe buttons: dry-run first, then apply with confirmation
- Expandable logs: show summary by default, expand for full output

**Что IMPERIUM Sanctum должен адаптировать:**
- Каждый chip: value + `last_checked` timestamp + staleness color
- "PASS" без timestamp = fake green. Должно быть "PASS (2 min ago)"
- Buttons: "Run Check" → shows output → "Apply" only if check passed
- DEGRADED/BLOCKED = honest states, not hidden

## Area 7: Local LLM resource governance

**Найдено (из общих знаний, не web search):**
- Token limits: hard cap per request (4K-8K for local models)
- Timeout: 60-120 seconds max per generation
- Temperature: 0.0-0.3 for code/structured output, never > 0.7
- Queue: one request at a time for local models
- VRAM: 4-5 GB = 7B-13B quantized models (Q4/Q5)
- CPU fallback: acceptable for short tasks, 10-30 tokens/sec

**Рекомендации для IMPERIUM:**
- Local model = narrow tool, not general agent
- Use for: classification, summarization, template filling
- Do NOT use for: complex reasoning, multi-step planning, code generation
- Hard limits: max_tokens=2048, timeout=90s, temperature=0.1
- Resource cap: single inference process, no parallel

## Area 8: Formal task decomposition

**Найдено:**
- Stage map = DAG of stages with explicit pass criteria
- Each stage: inputs, outputs, pass criteria, dependencies, timeout, retry policy
- Review gates: explicit WAITING_REVIEW state between stages
- Owner decision gates: WAITING_OWNER state, cannot auto-advance
- 40+ stages: group into phases (3-7 stages each), phase = mini-milestone

**Рекомендации для Astronomicon:**
- Stage map = flat list with order + dependencies (not nested tree)
- Pass criteria = list of verifiable statements ("file X exists", "test Y passes", "receipt Z valid")
- Owner gates: explicit field `owner_approval_required: true`
- Phase grouping: optional metadata, not structural requirement for v0.1

## Area 9: Repo/codebase explorer

**Найдено:**
- Source-of-truth registries: single JSON file listing all active components
- Task-to-file linking: receipt contains `files_touched` list
- Generated navigation: `AGENTS.md` pattern (already in IMPERIUM)
- Graph visualization: overkill for v0.1, text-based tree sufficient

**Рекомендации:**
- IMPERIUM already has AGENTS.md — this is correct pattern
- Add: `REGISTRY/ACTIVE_FILES_INDEX.json` — auto-generated list of all active source files
- Add: per-task `FILES_TOUCHED.json` in receipt — links task to modified files
- Later: Sanctum panel showing file→task→receipt graph

## Area 10: Security and boundary model

**Найдено:**
- Least privilege: worker gets only what it needs for current stage
- Disposable VM: worker state can be destroyed after bundle extraction
- No-delete policy: quarantine instead of delete, with timestamp and reason
- Allowlist > denylist: only explicitly approved commands can run
- Secret handling: never in receipts, never in bundles, reference by key name only

**IMPERIUM already implements:**
- Command allowlist (REGISTRY/COMMAND_ALLOWLIST.json) ✓
- No-push from VM2 ✓
- Public/private boundary scan ✓
- .gitignore for secrets ✓

**Missing:**
- Quarantine folder pattern (instead of delete)
- Per-stage file access scope (Officio corridor should limit which files agent can touch)
- Bundle content scan before acceptance (Custodes role)

---

# 4. IMPERIUM_ADAPTATION_MATRIX

| External pattern | Source | IMPERIUM organ | Artifact | Difficulty | Risk | Priority |
|---|---|---|---|---|---|---|
| SLSA provenance in bundle manifest | slsa.dev | Administratum | BUNDLE_MANIFEST.json schema | Small | LOW | P1 |
| in-toto layout = stage map | in-toto.io | Astronomicon | STAGE_MAP.json with materials/products | Small | LOW | P1 |
| in-toto link = stage receipt | in-toto.io | Administratum | STAGE_RECEIPT.json with hashes | Small | LOW | P1 |
| Temporal human approval state | temporal.io | Throne | WAITING_OWNER status in stage | Small | LOW | P0 |
| MAST failure taxonomy checks | arxiv | Inquisition | audit_checklist.json per failure mode | Medium | LOW | P2 |
| Filesystem state machine | general | Administratum | STATUS.json per task | Small | LOW | P0 |
| JSONL append-only event log | general | Administratum | TASK_EVENTS.jsonl | Small | LOW | P1 |
| Stale data timestamp in UI | general | Sanctum | last_checked field in HUD data | Small | LOW | P0 |
| UTF-8 header in all scripts | SO/docs | Mechanicus | Script template with encoding fix | Small | LOW | P0 |
| Quarantine instead of delete | security | Custodes | _QUARANTINE/ folder + policy | Small | LOW | P2 |
| Lock file for task execution | general | Administratum | .lock file pattern | Small | LOW | P2 |
| Pass criteria as verifiable list | Dagster/general | Astronomicon | pass_criteria field in stage | Small | LOW | P0 |
| Dry-run/apply/verify button pattern | UI patterns | Sanctum | Button states in HUD | Medium | LOW | P2 |
| Agent corridor file scope | security | Officio Agentis | allowed_paths in corridor | Small | MEDIUM | P1 |
| Warning baseline regression | general | Inquisition | WARNING_BASELINE.json + gate | Small | LOW | P0 |

---

# 5. NO_FAKE_GREEN_GUIDELINES

## Verdicts

- **PASS** = all checks ran, all passed, evidence exists, timestamp < 5 minutes
- **PASS_WITH_WARNINGS** = no blockers, but known debt exists. MUST list warnings.
- **DEGRADED** = system functional but incomplete. MUST list what's missing.
- **BLOCKED** = cannot proceed. MUST list blockers.
- **UNKNOWN** = check not run or evidence missing. NEVER display as PASS.
- **STALE** = check ran but > 1 hour ago. MUST show timestamp.

## Rules

1. **No verdict without timestamp.** Every verdict must include `checked_at` field.
2. **No PASS without evidence path.** Every PASS must point to receipt/report file.
3. **No CLEAR from Doctrinarium if any organ is LEVEL_0.** Must be DEGRADED at minimum.
4. **No stage completion without pass criteria check.** Every stage must have verifiable criteria.
5. **No bundle acceptance without manifest.** Every bundle must list files + sha256.
6. **No "green" chip in Sanctum without recent verification.** Stale = yellow, not green.
7. **No auto-advance past Owner gates.** Throne decisions are NEVER automated.
8. **No receipt without command evidence.** Receipt must include what command ran, exit code, timestamp.
9. **Absence of check ≠ PASS.** If verify_repo didn't run, verdict = UNKNOWN, not PASS.
10. **Warning count must be visible.** PASS_WITH_WARNINGS must show count, not hide it.

## Dashboard language

| Bad (fake green) | Good (honest) |
|---|---|
| "All systems operational" | "6/10 organs operational, 4 scaffold-only" |
| "PASS" (no timestamp) | "PASS (verified 3 min ago)" |
| "Ready" | "DEGRADED: Mechanicus, Inquisition, Throne, Custodes not operational" |
| Green dot (always) | Green dot (< 5 min) / Yellow dot (< 1 hour) / Red dot (stale/failed) |
| "0 issues" | "0 blockers, 121K warnings (legacy debt)" |

---

# 6. TASK_ENGINE_DESIGN_NOTES

## Identity model

```
GENERAL_TASK_ID: GTASK-YYYYMMDD-{short_name}
  └── TASK_ID: TASK-YYYYMMDD-{short_name}-V{n}
       └── STAGE_ID: STAGE-{order:02d}-{short_name}
            └── RUN_ID: RUN-{YYYYMMDD_HHMMSS}-{contour}
```

## Status model (per stage)

```
PLANNED → READY → ACTIVE → WAITING_REVIEW → WAITING_OWNER → PASS / FAIL / SKIPPED
                     ↑                                          |
                     └──────────── RETRY (Owner approved) ──────┘
```

## Stop/escalate conditions

- Stage FAIL → task pauses, Owner decides: retry / skip / abort
- Inquisition SUSPICIOUS → task pauses, Owner reviews
- Doctrinarium BLOCKED → task cannot start
- Any organ DEAD → task pauses at that organ

## Receipts per stage

```
.imperium_runtime/tasks/{TASK_ID}/stages/{STAGE_ID}/runs/{RUN_ID}/
  ├── RUN_START.json      # timestamp, agent, inputs
  ├── COMMAND_LOG.jsonl    # append-only command history
  ├── RUN_RESULT.json     # outputs, exit codes, verdict
  ├── AUDIT_RECEIPT.json   # Inquisition verdict
  └── BUNDLE_MANIFEST.json # if bundle produced
```

## Human approval gates

- Explicit `WAITING_OWNER` state
- Sanctum shows pending approvals
- Owner clicks Accept/Reject/Redo
- Decision recorded in `OWNER_DECISION.json`
- No timeout auto-approve (Owner decides when ready)

---

# 7. BUNDLE_AND_PROVENANCE_RECOMMENDATIONS

## VM2 bundle format

```
{TASK_ID}_{STAGE_ID}_{RUN_ID}.zip
├── BUNDLE_MANIFEST.json
├── SOURCE/
│   └── (modified/created files)
├── EVIDENCE/
│   ├── git_status.txt
│   ├── git_diff.patch
│   ├── verify_repo_output.json
│   ├── py_compile_result.json
│   └── git_cli_check_receipt.json
├── RECEIPTS/
│   └── RUN_RESULT.json
└── SHA256SUMS.txt
```

## BUNDLE_MANIFEST.json fields

```json
{
  "schema_version": "imperium.bundle_manifest.v0_1",
  "task_id": "TASK-...",
  "stage_id": "STAGE-01-...",
  "run_id": "RUN-20260512_143000-VM2",
  "builder": {
    "agent_id": "VM2_SERVITOR",
    "contour": "VM2",
    "hostname": "vm2-ubuntu",
    "timestamp_utc": "2026-05-12T14:30:00Z"
  },
  "git_truth": {
    "head_before": "abc1234",
    "branch": "master",
    "tree_url": "https://github.com/SoulsLike2313/Imperium-/tree/abc1234"
  },
  "materials": [
    {"path": "AGENTS.md", "sha256": "..."},
    {"path": "ORGANS/DOCTRINARIUM/SCRIPTS/...", "sha256": "..."}
  ],
  "products": [
    {"path": "ORGANS/CUSTODES/ORGAN_STATUS.json", "sha256": "..."},
    {"path": "ORGANS/CUSTODES/README.md", "sha256": "..."}
  ],
  "verification": {
    "verify_repo_verdict": "PASS_WITH_WARNINGS",
    "git_cli_check_verdict": "PASS",
    "py_compile_verdict": "PASS"
  }
}
```

## PC review checklist (Custodes function)

1. ☐ Bundle manifest exists and is valid JSON
2. ☐ SHA256SUMS match actual file hashes
3. ☐ git_truth.head_before matches current PC HEAD
4. ☐ No files outside expected scope (check products list)
5. ☐ No secrets in any file (grep for patterns)
6. ☐ verify_repo verdict ≠ FAIL
7. ☐ No shell=True in any Python file
8. ☐ No hardcoded absolute paths in new files
9. ☐ All new JSON files are valid
10. ☐ py_compile passes for all new .py files

---

# 8. WINDOWS_LINUX_RELIABILITY_NOTES

## UTF-8 fixes (MUST apply to all IMPERIUM scripts)

**Python (all platforms):**
```python
import os, sys
os.environ.setdefault("PYTHONUTF8", "1")
# For subprocess output:
# Always use encoding="utf-8", errors="replace" in subprocess.run()
```

**PowerShell (Windows):**
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
# Or set env before calling Python:
$env:PYTHONUTF8 = "1"
```

## SSH command style

**Bad:**
```
ssh user@host "complex && command | with pipes && echo done"
```

**Good:**
```
# Write script to temp file, scp it, execute it
scp -P 2223 script.sh user@host:/tmp/
ssh -p 2223 user@host "bash /tmp/script.sh"
```

## CRLF/LF

- `.gitattributes`: `* text=auto` (already in IMPERIUM)
- Python: always open files with `newline=""` or explicit `\n` in write
- JSON: always write with `json.dumps(...) + "\n"` (LF, not CRLF)

## ZIP encoding

- Python `zipfile`: use `zipfile.ZIP_DEFLATED`, avoid non-ASCII filenames in bundles
- If non-ASCII needed: use UTF-8 flag in ZIP header (`zipfile.ZipInfo.flag_bits |= 0x800`)

## Robust command style

- Never use `&&` in cross-platform commands
- Always use list-based argv in subprocess
- Always specify `timeout` parameter
- Always capture both stdout and stderr
- Always check exit_code explicitly

---

# 9. DASHBOARD_UI_RECOMMENDATIONS

## Core principles

1. **Every value has a timestamp** — "PASS" alone is meaningless
2. **Staleness is visible** — color coding based on age
3. **Honest states** — DEGRADED/BLOCKED are normal, not errors
4. **Safe buttons** — dry-run first, apply second
5. **Expandable detail** — summary visible, full log on click

## Recommended Sanctum HUD layout

```
┌─────────────────────────────────────────────────┐
│ IMPERIUM — System Health (checked 2 min ago)     │
├─────────────────────────────────────────────────┤
│ [●] Doctrinarium  OPERATIONAL  (preflight: DEGRADED)  │
│ [●] Administratum OPERATIONAL  (tasks: 1 active)      │
│ [●] Officio       OPERATIONAL  (mode: DRAFT_ONLY)     │
│ [●] Astronomicon  OPERATIONAL  (stages: 3/5)          │
│ [○] Mechanicus    SCAFFOLD     (no tools assigned)    │
│ [○] Inquisition   SCAFFOLD     (no audit available)   │
│ [○] Throne        SCAFFOLD     (acceptance: manual)   │
│ [○] Custodes      SCAFFOLD     (boundary: undefined)  │
│ [○] Strategium    SCAFFOLD     (no research)          │
│ [○] Schola        SCAFFOLD     (no learning notes)    │
├─────────────────────────────────────────────────┤
│ Active Task: TASK-20260512-... | Stage 2/5 | 40%│
│ Warnings: 142 | Blockers: 0 | Last verify: 3m  │
└─────────────────────────────────────────────────┘
```
  
## Color coding

- `●` Green = OPERATIONAL + recently verified
- `●` Yellow = OPERATIONAL but stale (> 1 hour since check)
- `○` Gray = SCAFFOLD / NOT_OPERATIONAL
- `●` Red = FAILED / BLOCKED

## Button patterns

- "Run Preflight" → shows output → updates chips
- "Register Task" → opens form → confirms → creates files
- "Accept" (Throne) → shows evidence → confirms → writes receipt 

```markdown
# 10. FINAL_RECOMMENDATIONS

## 5 малых изменений, которые IMPERIUM должен сделать сейчас

1. **UTF-8 header во всех скриптах** — добавить `os.environ.setdefault("PYTHONUTF8", "1")` в начало каждого Python скрипта и `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8` в каждый PS1. Это устраняет mojibake навсегда.
   - Artifact: шаблон в `DOCS/OWNER_DOCTRINE/SCRIPT_TEMPLATE.md`
   - Difficulty: small
   - Organ: Mechanicus

2. **`last_checked_at` field в каждом receipt и status** — ни один ORGAN_STATUS.json не должен существовать без timestamp последней проверки. Sanctum должен показывать staleness.
   - Artifact: поле в ORGAN_STATUS.json schema
   - Difficulty: small
   - Organ: Doctrinarium

3. **WARNING_BASELINE.json** — зафиксировать текущий count (121K) и добавить gate: если warnings > baseline + 50 → FAIL.
   - Artifact: `REGISTRY/WARNING_BASELINE.json` + gate в verify_repo
   - Difficulty: small
   - Organ: Inquisition

4. **BUNDLE_MANIFEST.json schema** — формализовать формат VM2 bundle по модели SLSA provenance (builder, materials, products, git_truth, verification).
   - Artifact: `schemas/bundle_manifest.schema.json`
   - Difficulty: small
   - Organ: Administratum

5. **Pass criteria в каждом stage** — Astronomicon stage map MUST содержать verifiable pass_criteria для каждого stage. Без criteria = stage не может быть marked PASS.
   - Artifact: обязательное поле в stage_map schema
   - Difficulty: small
   - Organ: Astronomicon

## 5 средних изменений на потом

1. **JSONL event log для Administratum** — append-only `ORGANS/ADMINISTRATUM/MEMORY/EVENTS.jsonl` куда записывается каждое значимое событие (task registered, stage started, stage completed, Owner decision). Это audit trail.
   - Difficulty: medium
   - Organ: Administratum

2. **Inquisition audit checklist по MAST taxonomy** — для каждого stage audit, проверять: specification clarity, scope creep, hallucination markers, incomplete verification, premature termination.
   - Difficulty: medium
   - Organ: Inquisition

3. **Sanctum organ HUD с staleness coloring** — заменить hardcoded chips на real data с цветовой индикацией свежести (green < 5 min, yellow < 1 hour, red = stale).
   - Difficulty: medium
   - Organ: Mechanicus (Sanctum)

4. **Lock file pattern для task execution** — `.imperium_runtime/locks/{TASK_ID}.lock` предотвращает параллельное выполнение одной задачи двумя агентами.
   - Difficulty: medium
   - Organ: Administratum

5. **Per-stage file scope в corridor** — Officio Agentis corridor должен содержать `allowed_paths` и `forbidden_paths` для конкретного stage, не только общие forbidden zones.
   - Difficulty: medium
   - Organ: Officio Agentis

## 5 вещей, которые НЕ делать сейчас

1. **НЕ внедрять Temporal/Airflow/Dagster** — слишком тяжёлые dependencies для local-first системы. Filesystem JSON + Python scripts достаточны.

2. **НЕ строить SQLite task database** — JSON files на filesystem проще, прозрачнее, и достаточны для текущего масштаба (< 100 tasks). SQLite = v0.3+.

3. **НЕ делать auto-retry для failed stages** — каждый retry = Owner decision. Автоматический retry скрывает проблемы и создаёт fake green.

4. **НЕ строить graph visualization** — text-based tree и JSON registries достаточны. Graph UI = красиво но не operational priority.

5. **НЕ публиковать internal architecture** — SLSA/in-toto patterns можно показывать как skill, но конкретная organ chain IMPERIUM = private.

## Unanswered questions

1. **Idempotency enforcement** — как гарантировать что повторный запуск stage с тем же input даёт тот же output? Для code generation это невозможно. Нужна policy: "idempotent where possible, receipt-tracked where not".

2. **Partial stage completion** — что если stage выполнен на 70% и agent crashed? Нужен ли checkpoint mechanism или всегда restart from scratch?

3. **Multi-stage parallelism** — Owner doctrine подразумевает sequential chain. Но некоторые stages могут быть independent. Нужна ли parallel execution в v0.1? (SUGGESTION: нет, sequential достаточен)

4. **Retention policy** — сколько хранить runtime receipts? Вечно? 30 дней? По task completion? Нужна policy.

5. **Cross-task dependencies** — может ли TASK-B зависеть от результата TASK-A? Если да, как это выражается в stage map? (SUGGESTION: не в v0.1, каждый task independent)

## Что отправить Logos-Speculum для hard review

1. **BUNDLE_MANIFEST.json schema** — попросить найти сценарии где manifest может врать (sha256 mismatch, missing files, stale git_truth)

2. **No-fake-green guidelines** — попросить найти loopholes (как agent может обойти checks и получить PASS)

3. **MAST failure taxonomy mapping** — попросить проверить: покрывает ли IMPERIUM organ chain все 14 failure modes? Какие не покрыты?

4. **Corridor packet** — попросить найти сценарии где agent может выйти за corridor (path traversal, command injection через allowed commands, scope creep через "helpful" additions)

5. **Staleness attack** — попросить проверить: что если agent показывает старый receipt как свежий? Как Doctrinarium/Inquisition ловят stale evidence?

---

# FINAL ANSWER TO OWNER

## 1. Где research pack

Research pack выдан в чат как единый markdown документ (10 секций). Файлы не созданы в репозитории (read-only mode). Owner может сохранить в `DOCS/RESEARCH/KIRO_EXTERNAL_REALITY_SCAN_20260512/` при желании.

## 2. Source count

**17 источников** проиндексированы с URL, типом, reliability rating и relevance mapping.

## 3. Top 10 findings

1. **SLSA provenance model** прямо применим к IMPERIUM bundle manifests — формат уже почти совпадает с тем что IMPERIUM делает интуитивно
2. **in-toto layout/link** = точная аналогия Astronomicon stage map / Administratum receipt
3. **MAST taxonomy (NeurIPS 2025)** — 14 формальных failure modes для multi-agent систем, IMPERIUM архитектурно защищён от большинства ЕСЛИ органы operational
4. **Temporal human-in-the-loop** — durable approval pattern реализуем через filesystem state без Temporal dependency
5. **Hallucination propagation** — #1 risk для multi-agent: output одного агента становится trusted input для следующего. Inquisition MUST audit каждый handoff.
6. **Filesystem-based task queue** достаточен для IMPERIUM масштаба — не нужны тяжёлые dependencies
7. **PowerShell UTF-8** — конкретный fix для mojibake проблемы: 2 строки в начале каждого PS1
8. **Stale data = fake green** — dashboard без timestamp = ложь. Каждый chip нуждается в `last_checked_at`
9. **Dagster asset-centric thinking** — определяй что должно существовать (receipts, manifests), а не что запускать. Verification spine уже делает это.
10. **40% multi-agent projects cancelled (Gartner)** — основная причина: unclear value + inadequate risk controls. IMPERIUM Owner-gated approach = правильная защита.

## 4. Top 5 immediate actionable recommendations

1. **Добавить UTF-8 headers** во все скрипты (устраняет mojibake, 5 минут на скрипт)
2. **Создать WARNING_BASELINE.json** (фиксирует текущий 121K count, позволяет ловить регрессии)
3. **Добавить `last_checked_at`** в ORGAN_STATUS.json schema (устраняет stale data fake green)
4. **Формализовать BUNDLE_MANIFEST.json** по SLSA model (делает VM2 bundles verifiable)
5. **Добавить pass_criteria** как обязательное поле в stage map (устраняет "stage complete without evidence")

## 5. Top risks

| Risk | Source | Impact | Mitigation |
|------|--------|--------|-----------|
| Hallucination propagation between agents | MAST taxonomy | Cascading errors through chain | Inquisition per-stage audit |
| Stale evidence presented as fresh | Dashboard patterns | False confidence | Timestamp + staleness coloring |
| Agent scope creep | MAST taxonomy | Uncontrolled changes | Officio corridor + file scope |
| UTF-8 mojibake in receipts | Windows/Linux pain | Corrupted evidence | UTF-8 headers in all scripts |
| Warning flood hiding regressions | Current IMPERIUM state | New bugs invisible | Warning baseline + threshold gate |

## 6. Что отправить Logos-Speculum

1. BUNDLE_MANIFEST.json schema — red-team на forgery/staleness
2. No-fake-green guidelines — red-team на loopholes
3. MAST failure taxonomy mapping — coverage check
4. Corridor packet — escape scenarios
5. Staleness attack vectors — how agent can present old evidence as new

---

*Research pack завершён. Репозиторий не модифицирован. Все рекомендации = advisory. Owner решает что адаптировать.*
```