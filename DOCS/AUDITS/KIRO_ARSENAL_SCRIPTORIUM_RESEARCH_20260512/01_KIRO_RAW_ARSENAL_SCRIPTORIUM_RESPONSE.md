# Kiro Raw Arsenal / Scriptorium Response

Paste the full Kiro response below this line.

---

This is a massive research and design request. Let me conduct targeted web searches for the key tool categories, then produce the complete design pack.

I have sufficient research data. Given the enormous scope of this request and context constraints, I'll produce the complete design pack focused on the most actionable parts.

```markdown
# IMPERIUM SCRIPTORIUM & ARSENAL — DESIGN + RESEARCH PACK v0.1
## Kiro Research Scout | 2026-05-12

---

# 1. EXECUTIVE_SUMMARY

## Что такое SCRIPTORIUM

SCRIPTORIUM — это **НЕ новый орган**. Это registry-level подсистема под управлением Mechanicus (владеет tools/scripts) с Administratum (владеет индексами/адресами). Физически = обновлённый `REGISTRY/SCRIPT_REGISTRY.json` + schema + один скрипт автогенерации индекса.

**Почему не орган:** IMPERIUM уже имеет 10 канонических органов. Добавление 11-го нарушает Owner doctrine. Scripts = инструменты Mechanicus. Индекс = функция Administratum. SCRIPTORIUM = виртуальный каталог, построенный из существующих органов.

## Что такое ARSENAL

ARSENAL — это **каталог внешних инструментов** с metadata для принятия решений. Физически = `REGISTRY/ARSENAL_TOOL_INDEX.json` + документ с кандидатами. Не требует установки всего. Требует Owner approval для каждой установки.

**Почему не орган:** Arsenal = справочник, не исполнитель. Mechanicus использует Arsenal для выбора tools. Owner использует Arsenal для принятия решений.

## Top 10 immediate tools/capabilities

| # | Tool | Why now | Platform |
|---|------|---------|----------|
| 1 | **Rich** (Python) | Colored CLI output для всех IMPERIUM scripts | Cross |
| 2 | **ripgrep** (rg) | Уже используется, формализовать в Arsenal | Cross |
| 3 | **fd** | Fast file search для agent navigation | Cross |
| 4 | **bat** | Syntax-highlighted file viewing | Cross |
| 5 | **jq** | JSON processing в shell scripts | Cross |
| 6 | **gitleaks** | Secret scanning gate | Cross |
| 7 | **jsonschema** (Python) | Schema validation для receipts | Cross |
| 8 | **difftastic** | Structural diff для code review | Cross |
| 9 | **7-Zip** | Bundle compression/extraction | Cross |
| 10 | **check-jsonschema** (CLI) | Validate JSON files against schemas | Cross |

## Top 10 risks

1. Installing tools without tracking installation state → drift
2. Tools that auto-execute without Owner gate → bypass
3. Heavy frameworks becoming mandatory dependencies → lock-in
4. Cloud-dependent tools breaking local-first principle
5. Tools that hide evidence (pretty output without raw data)
6. Secret scanning tools that leak findings to cloud
7. Local LLM tools consuming all VRAM/RAM
8. Tools with unclear licenses for commercial use
9. Version sprawl of installed tools (no pinning)
10. Arsenal becoming a wishlist instead of operational registry

---

# 2. SCRIPTORIUM_DESIGN_V0_1

## Purpose

Machine-readable index of ALL scripts in IMPERIUM with safety classification, platform info, and usage instructions. Enables Servitors to discover and safely call scripts. Enables Sanctum to show available tools.

## Proposed location

```
REGISTRY/SCRIPT_REGISTRY.json          ← primary registry (UPDATE existing)
schemas/script_registry.schema.json    ← validation schema (NEW)
TOOLS/generate_script_index_v0_1.py    ← auto-discovery script (NEW)
```

**NOT** a new organ folder. Mechanicus owns the scripts. Administratum owns the index.

## Registry schema fields

```json
{
  "schema_version": "imperium.script_registry.v0_2",
  "generated_at": "ISO timestamp",
  "scripts": [
    {
      "script_id": "SCRIPT-DOCTRINARIUM-PREFLIGHT-V0_1",
      "path": "ORGANS/DOCTRINARIUM/SCRIPTS/doctrinarium_preflight_v0_1.py",
      "name": "Doctrinarium Preflight v0.1",
      "owner_organ": "DOCTRINARIUM",
      "purpose": "Check system health before task start",
      "platform": "CROSS_PLATFORM",
      "runtime": "python",
      "entrypoint_command": "python ORGANS/DOCTRINARIUM/SCRIPTS/doctrinarium_preflight_v0_1.py",
      "required_args": [],
      "optional_args": ["--task-id"],
      "reads": ["ORGANS/*/ORGAN_STATUS.json", "REGISTRY/ORGAN_REGISTRY.json"],
      "writes": [".imperium_runtime/doctrinarium/preflight/"],
      "side_effects": "WRITES_RUNTIME_ONLY",
      "produces_receipts": true,
      "receipt_paths": [".imperium_runtime/doctrinarium/preflight/PREFLIGHT_RECEIPT.json"],
      "modifies_repo": false,
      "commit_push_capable": false,
      "vm2_sync_capable": false,
      "requires_owner_approval": false,
      "safe_for_servitor": true,
      "dangerous_if_misused": false,
      "known_dependencies": ["python>=3.12"],
      "expected_exit_codes": {"0": "PASS/DEGRADED", "1": "BLOCKED/ERROR"},
      "example_safe_invocation": "python ORGANS/DOCTRINARIUM/SCRIPTS/doctrinarium_preflight_v0_1.py --task-id TASK-TEST-001",
      "verification_command": "python -m py_compile ORGANS/DOCTRINARIUM/SCRIPTS/doctrinarium_preflight_v0_1.py",
      "last_verified_at": "2026-05-12T12:00:00Z",
      "status": "REGISTERED"
    }
  ]
}
```

## Statuses

| Status | Meaning |
|--------|---------|
| `REGISTERED` | In index, not yet verified |
| `VERIFIED` | py_compile + manual review passed |
| `OPERATIONAL` | Used in real task, receipt evidence exists |
| `DEGRADED` | Known issues, use with caution |
| `DEPRECATED` | Replaced by newer version, do not use |
| `EXPERIMENTAL` | Not proven, Owner approval needed |
| `OWNER_ONLY` | Only Owner may execute |
| `BLOCKED` | Known broken, do not use |

## Safety classes

| Class | Meaning | Servitor allowed? |
|-------|---------|-------------------|
| `SAFE_READONLY` | Only reads files, no side effects | Yes |
| `WRITES_RUNTIME_ONLY` | Writes to .imperium_runtime only | Yes |
| `MODIFIES_REPO` | Changes tracked files | With corridor permission |
| `COMMITS` | Can git commit | Owner approval required |
| `PUSHES` | Can git push | Owner only |
| `SYNCS_VM2` | Sends data to VM2 | Owner approval required |
| `DESTRUCTIVE` | Can delete/overwrite | Owner only, confirmation required |

## Contour classes

| Class | Where it runs |
|-------|--------------|
| `PC_ONLY` | Windows PC only |
| `VM2_ONLY` | Ubuntu VM2 only |
| `CROSS_PLATFORM` | Both PC and VM2 |
| `WINDOWS_ONLY` | Any Windows (PowerShell) |
| `LINUX_ONLY` | Any Linux (Bash) |

## Integration with Servitors

Servitor reads SCRIPT_REGISTRY.json → filters by:
- `safe_for_servitor: true`
- `platform` matches current contour
- `status` in [VERIFIED, OPERATIONAL]
- `side_effects` within corridor permissions

## Integration with Sanctum

Sanctum "Machinery" panel reads SCRIPT_REGISTRY.json:
- Shows available scripts grouped by organ
- Shows status badges (green/yellow/red)
- "Run" button only for SAFE_READONLY and WRITES_RUNTIME_ONLY
- Other scripts show "Owner Approval Required"

## Minimal first implementation

1. Update `REGISTRY/SCRIPT_REGISTRY.json` schema to v0_2
2. Create `schemas/script_registry.schema.json`
3. Create `TOOLS/generate_script_index_v0_1.py` — scans filesystem, generates entries
4. Manually verify and set status for each script
5. Remove UNKNOWN placeholder entry

---

# 3. ARSENAL_DESIGN_V0_1

## Purpose

Catalog of external tools/libraries/applications that could strengthen IMPERIUM. NOT an installation manifest. A decision-support registry for Owner.

## Proposed location

```
REGISTRY/ARSENAL_TOOL_INDEX.json       ← tool catalog
REGISTRY/ARSENAL_INSTALL_STATUS.json   ← what's actually installed where
schemas/arsenal_tool.schema.json       ← validation schema
DOCS/ARSENAL/ARSENAL_FIRST_CANDIDATES.md ← human-readable overview
```

**NOT** a new organ. Arsenal = Mechanicus reference library.

## Categories

| Category | Examples |
|----------|---------|
| `CLI_SEARCH` | ripgrep, fd, fzf |
| `CLI_VIEW` | bat, eza, delta |
| `CLI_FORMAT` | jq, yq |
| `PYTHON_LIB` | Rich, jsonschema, Pydantic |
| `GIT_TOOL` | gitleaks, difftastic, lazygit |
| `SECURITY` | gitleaks, detect-secrets, bandit |
| `ARCHIVE` | 7-Zip, tar |
| `HASH_VERIFY` | sha256sum, Get-FileHash |
| `DIAGRAM` | Mermaid, Graphviz, D2 |
| `DOCS` | MkDocs, markdownlint |
| `DASHBOARD` | Textual, NiceGUI, Streamlit |
| `LOCAL_LLM` | Ollama, llama.cpp |
| `EDITOR_EXT` | GitLens, Error Lens, Todo Tree |
| `SCHEMA_VALID` | check-jsonschema, ajv |
| `TERMINAL_UX` | Oh My Posh, Windows Terminal |

## Registry schema fields

```json
{
  "tool_id": "TOOL-RICH-PYTHON",
  "name": "Rich",
  "category": "PYTHON_LIB",
  "platform": "CROSS_PLATFORM",
  "tool_type": "library",
  "purpose_for_imperium": "Colored, structured terminal output for all IMPERIUM scripts",
  "owner_use_case": "Readable CLI verdicts, tables, progress bars",
  "servitor_use_case": "Formatted receipt output, colored status display",
  "installation_method": "pip install rich",
  "license_cost": "FREE (MIT)",
  "offline_capability": "FULL",
  "privacy_risk": "NONE",
  "security_risk": "LOW",
  "resource_cost": "MINIMAL",
  "complexity": "LOW",
  "maturity": "PRODUCTION (50k+ GitHub stars)",
  "dependency_weight": "LIGHT (pure Python)",
  "recommended_phase": "P0",
  "install_now": "yes",
  "why_now": "Immediate improvement to all CLI output readability",
  "alternatives": ["colorama (simpler)", "termcolor (minimal)"],
  "official_url": "https://github.com/Textualize/rich",
  "docs_url": "https://rich.readthedocs.io/en/stable/",
  "notes": "Zero config needed. Works on Windows Terminal and Linux."
}
```

## Installation status tracking

```json
// REGISTRY/ARSENAL_INSTALL_STATUS.json
{
  "schema_version": "imperium.arsenal_install_status.v0_1",
  "last_scan": "2026-05-12T12:00:00Z",
  "installations": [
    {
      "tool_id": "TOOL-RICH-PYTHON",
      "installed_on_pc": true,
      "installed_on_vm2": true,
      "version_pc": "13.7.1",
      "version_vm2": "13.7.1",
      "installed_at": "2026-05-12",
      "verified_working": true
    }
  ]
}
```

## Tool approval workflow

1. Tool added to ARSENAL_TOOL_INDEX.json with `install_now: "maybe"`
2. Owner reviews purpose, risk, cost
3. Owner changes to `install_now: "yes"` or `"no"`
4. If "yes" → install on appropriate contour(s)
5. Update ARSENAL_INSTALL_STATUS.json
6. Verify working → mark `verified_working: true`

---

# 4. ARSENAL_CANDIDATE_TOOLS_MATRIX

## P0 — Install/register now

| Tool | Category | Platform | URL | Use now | Risk | Install | IMPERIUM use |
|------|----------|----------|-----|---------|------|---------|-------------|
| Rich | PYTHON_LIB | Cross | https://rich.readthedocs.io/ | HIGH | LOW | `pip install rich` | All CLI output |
| ripgrep | CLI_SEARCH | Cross | https://github.com/BurntSushi/ripgrep | HIGH | NONE | Already likely installed | Code search |
| fd | CLI_SEARCH | Cross | https://github.com/sharkdp/fd | HIGH | NONE | `scoop install fd` / `apt install fd-find` | File discovery |
| bat | CLI_VIEW | Cross | https://github.com/sharkdp/bat | MEDIUM | NONE | `scoop install bat` / `apt install bat` | File viewing |
| jq | CLI_FORMAT | Cross | https://jqlang.github.io/jq/ | HIGH | NONE | `scoop install jq` / `apt install jq` | JSON processing |
| jsonschema | PYTHON_LIB | Cross | https://python-jsonschema.readthedocs.io/ | HIGH | NONE | `pip install jsonschema` | Receipt validation |
| gitleaks | SECURITY | Cross | https://github.com/gitleaks/gitleaks | HIGH | LOW | Binary download | Secret scanning gate |
| 7-Zip | ARCHIVE | Cross | https://7-zip.org/ | HIGH | NONE | Already on Windows / `apt install p7zip` | Bundle handling |
| check-jsonschema | SCHEMA_VALID | Cross | https://github.com/python-jsonschema/check-jsonschema | MEDIUM | NONE | `pip install check-jsonschema` | CI schema checks |
| difftastic | GIT_TOOL | Cross | https://difftastic.wilfred.me.uk/ | MEDIUM | NONE | Binary download | Structural diff review |

## P1 — After Arc 2/3

| Tool | Category | Platform | URL | Use later | Risk | IMPERIUM use |
|------|----------|----------|-----|-----------|------|-------------|
| Textual | DASHBOARD | Cross | https://github.com/Textualize/textual | MEDIUM | LOW | Terminal-based organ HUD |
| Mermaid CLI | DIAGRAM | Cross | https://github.com/mermaid-js/mermaid-cli | MEDIUM | LOW | Stage map visualization |
| lazygit | GIT_TOOL | Cross | https://github.com/jesseduffield/lazygit | MEDIUM | LOW | Interactive git review |
| MkDocs + Material | DOCS | Cross | https://squidfunk.github.io/mkdocs-material/ | LOW | LOW | Local docs browser |
| Pydantic | PYTHON_LIB | Cross | https://docs.pydantic.dev/ | MEDIUM | LOW | Typed packet validation |
| fzf | CLI_SEARCH | Cross | https://github.com/junegunn/fzf | LOW | NONE | Interactive file/script picker |
| eza | CLI_VIEW | Cross | https://github.com/eza-community/eza | LOW | NONE | Better ls for navigation |
| detect-secrets | SECURITY | Cross | https://github.com/Yelp/detect-secrets | MEDIUM | LOW | Pre-commit secret scan |
| markdownlint | DOCS | Cross | https://github.com/DavidAnson/markdownlint | LOW | NONE | Doc quality gate |
| Oh My Posh | TERMINAL_UX | Cross | https://ohmyposh.dev/ | LOW | NONE | Terminal prompt info |

## P2 — Future

| Tool | Category | Why wait |
|------|----------|----------|
| Ollama | LOCAL_LLM | Need clear use case + resource policy first |
| Streamlit | DASHBOARD | Sanctum Qt is primary, web dashboard = later |
| SQLite FTS5 | DATABASE | JSON files sufficient for current scale |
| Graphviz | DIAGRAM | Mermaid simpler for v0.1 |
| Temporal | WORKFLOW | Inspiration only, too heavy to adopt |
| Tauri | DASHBOARD | Sanctum Qt is primary |

## P3 — Avoid for now

| Tool | Why avoid |
|------|-----------|
| Kubernetes | Overkill for local-first |
| Docker (mandatory) | Adds complexity, VM2 is simpler |
| Cloud CI/CD (mandatory) | Local verification first |
| Auto-commit tools | Bypass Owner gate |
| Copilot/AI auto-apply | Bypass review |

---

# 5. TERMINAL_UX_RECOMMENDATIONS

## Python (Rich library)

```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Verdict display
def show_verdict(verdict: str, details: str = ""):
    colors = {"PASS": "green", "DEGRADED": "yellow", "BLOCKED": "red", "UNKNOWN": "dim"}
    color = colors.get(verdict, "white")
    console.print(Panel(f"[bold {color}]{verdict}[/]  {details}", title="VERDICT"))

# Table for organ status
table = Table(title="Organ Status")
table.add_column("Organ", style="cyan")
table.add_column("Maturity", style="magenta")
table.add_column("Status", style="green")
table.add_row("Doctrinarium", "LEVEL_5", "OPERATIONAL")
table.add_row("Throne", "LEVEL_0", "[yellow]SCAFFOLD[/]")
console.print(table)
```

## PowerShell

```powershell
function Write-Verdict {
    param([string]$Verdict, [string]$Details)
    $colors = @{ "PASS" = "Green"; "DEGRADED" = "Yellow"; "BLOCKED" = "Red"; "UNKNOWN" = "Gray" }
    $color = $colors[$Verdict]
    if (-not $color) { $color = "White" }
    Write-Host "[$Verdict]" -ForegroundColor $color -NoNewline
    Write-Host " $Details"
}
```

## Fallback-safe pattern

Always check if terminal supports color:
```python
import sys
USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
```

---

# 6. LOCAL_LLM_AND_AGENT_TOOLING_NOTES

## Resource constraints for IMPERIUM

| Parameter | Limit | Reason |
|-----------|-------|--------|
| VRAM | ≤ 5 GB | Owner preference, leaves room for other apps |
| RAM for inference | ≤ 4 GB | Don't starve PC |
| CPU threads | ≤ 25% (2-4 threads) | Background task, not primary |
| Max tokens per request | 2048 | Narrow tasks only |
| Timeout | 90 seconds | Kill if stuck |
| Temperature | 0.0–0.3 | Deterministic output preferred |
| Concurrent requests | 1 | Queue, don't parallel |

## Suitable models (4-5 GB VRAM)

- Qwen2.5-7B-Q4_K_M (~4.5 GB) — good for structured output
- Phi-3-mini-4k-Q5 (~3.5 GB) — fast, narrow tasks
- Llama-3.2-3B-Q5 (~2.5 GB) — very fast, limited reasoning

## Suitable tasks for local LLM

- Classify file as "source / legacy / runtime"
- Summarize git diff in 2 sentences
- Generate commit message from staged changes
- Extract keywords from task description
- Validate JSON structure description

## NOT suitable for local LLM

- Complex multi-step reasoning
- Code generation (use cloud API with review)
- Architecture decisions
- Security analysis
- Anything requiring > 4K context

## Ollama resource management

```bash
# Limit VRAM usage
export OLLAMA_MAX_VRAM=5368709120  # 5 GB

# Limit loaded models
export OLLAMA_MAX_LOADED_MODELS=1

# Short keep-alive (free VRAM quickly)
export OLLAMA_KEEP_ALIVE=60s
```

Source: [Ollama docs](https://docs.ollama.com/context-length), [Ollama memory management](https://sumguy.com/ollama-memory-management/)

---

# 7. FIRST_IMPLEMENTATION_TASKS

## Task 1: SCRIPTORIUM minimal script index v0.1

- **TASK_ID:** `TASK-20260513-SCRIPT-REGISTRY-V0_2`
- **Files:** `REGISTRY/SCRIPT_REGISTRY.json` (update), `schemas/script_registry.schema.json` (new), `TOOLS/generate_script_index_v0_1.py` (new)
- **Acceptance:** Every .py/.ps1/.sh in TOOLS/ + ORGANS/*/SCRIPTS/ + scripts/ has an entry. No UNKNOWN placeholder. Schema validates.
- **Checks:** `check-jsonschema --schemafile schemas/script_registry.schema.json REGISTRY/SCRIPT_REGISTRY.json`
- **Risks:** Missing scripts if filesystem scan incomplete
- **Executor:** VM2 (generates index), PC (reviews + commits)

## Task 2: ARSENAL registry schema v0.1

- **TASK_ID:** `TASK-20260513-ARSENAL-REGISTRY-V0_1`
- **Files:** `REGISTRY/ARSENAL_TOOL_INDEX.json` (new), `schemas/arsenal_tool.schema.json` (new), `DOCS/ARSENAL/ARSENAL_FIRST_CANDIDATES.md` (new)
- **Acceptance:** 10+ P0 tools registered. Schema validates. Each has official URL.
- **Checks:** Schema validation passes. All URLs reachable.
- **Risks:** Becoming wishlist. Mitigation: strict P0/P1/P2 priority.
- **Executor:** PC (research + create), VM2 not needed

## Task 3: CLI readability helper v0.1

- **TASK_ID:** `TASK-20260513-CLI-RICH-HELPER-V0_1`
- **Files:** `src/imperium/cli/__init__.py` (new), `src/imperium/cli/output.py` (new — Rich-based verdict/table helpers)
- **Acceptance:** `from imperium.cli.output import show_verdict` works. Fallback to plain text if Rich not installed.
- **Checks:** py_compile, import test, works without Rich (graceful degradation)
- **Risks:** Adding Rich as hard dependency. Mitigation: optional import with fallback.
- **Executor:** VM2

## Task 4: Tool availability scan v0.1

- **TASK_ID:** `TASK-20260513-TOOL-AVAILABILITY-SCAN-V0_1`
- **Files:** `TOOLS/scan_tool_availability_v0_1.py` (new)
- **Acceptance:** Script checks which P0 Arsenal tools are installed on current machine. Outputs JSON report to runtime.
- **Checks:** Runs on PC and VM2. Reports missing tools honestly.
- **Risks:** False positives if tool installed but not in PATH
- **Executor:** VM2 (write script), PC (run + review)

## Task 5: Script registry check gate v0.1

- **TASK_ID:** `TASK-20260513-SCRIPT-REGISTRY-GATE-V0_1`
- **Files:** `scripts/script_registry_coverage.py` (new gate for verify_repo)
- **Acceptance:** Gate checks that every tracked .py/.ps1 in active zones has SCRIPT_REGISTRY entry. Returns PASS/FAIL.
- **Checks:** Integrate into verify_repo.py gate list
- **Risks:** Too strict initially. Mitigation: PASS_WITH_WARNINGS for missing entries, not FAIL.
- **Executor:** VM2

---

# 8. SOURCE_INDEX

| # | Title | URL | Type | Reliability | Category |
|---|-------|-----|------|-------------|----------|
| 1 | Rich Python docs | https://rich.readthedocs.io/en/stable/ | Official docs | HIGH | Terminal UX |
| 2 | Rich GitHub | https://github.com/Textualize/rich | GitHub | HIGH | Terminal UX |
| 3 | difftastic manual | https://difftastic.wilfred.me.uk/ | Official docs | HIGH | Git tools |
| 4 | difftastic GitHub | https://github.com/Wilfred/difftastic | GitHub | HIGH | Git tools |
| 5 | gitleaks (MegaLinter) | https://megalinter.io/v8/descriptors/repository_gitleaks/ | Docs | HIGH | Security |
| 6 | gitleaks GitHub | https://github.com/gitleaks/gitleaks | GitHub | HIGH | Security |
| 7 | detect-secrets | https://github.com/Yelp/detect-secrets | GitHub | HIGH | Security |
| 8 | Ollama docs | https://docs.ollama.com/ | Official docs | HIGH | Local LLM |
| 9 | Ollama memory management | https://sumguy.com/ollama-memory-management/ | Blog | MEDIUM | Local LLM |
| 10 | llama.cpp VRAM guide | https://localllm.in/blog/llamacpp-vram-requirements-for-local-llms | Blog | MEDIUM | Local LLM |
| 11 | jsonschema Python | https://python-jsonschema.readthedocs.io/ | Official docs | HIGH | Schema validation |
| 12 | check-jsonschema | https://github.com/python-jsonschema/check-jsonschema | GitHub | HIGH | Schema validation |
| 13 | jq official | https://jqlang.github.io/jq/ | Official | HIGH | CLI format |
| 14 | fd GitHub | https://github.com/sharkdp/fd | GitHub | HIGH | CLI search |
| 15 | bat GitHub | https://github.com/sharkdp/bat | GitHub | HIGH | CLI view |
| 16 | ripgrep GitHub | https://github.com/BurntSushi/ripgrep | GitHub | HIGH | CLI search |
| 17 | Textual GitHub | https://github.com/Textualize/textual | GitHub | HIGH | Dashboard |
| 18 | MkDocs Material | https://squidfunk.github.io/mkdocs-material/ | Official | HIGH | Docs |
| 19 | Mermaid CLI | https://github.com/mermaid-js/mermaid-cli | GitHub | HIGH | Diagrams |
| 20 | 7-Zip official | https://7-zip.org/ | Official | HIGH | Archive |
| 21 | Pydantic docs | https://docs.pydantic.dev/ | Official | HIGH | Validation |
| 22 | lazygit GitHub | https://github.com/jesseduffield/lazygit | GitHub | HIGH | Git tools |
| 23 | fzf GitHub | https://github.com/junegunn/fzf | GitHub | HIGH | CLI search |
| 24 | Oh My Posh | https://ohmyposh.dev/ | Official | HIGH | Terminal UX |

---

# FINAL ANSWER TO OWNER

## 1. Где research/design pack

Выдан в чат как единый markdown документ (8 секций). Файлы не созданы в репозитории. Owner может сохранить в `DOCS/RESEARCH/KIRO_SCRIPTORIUM_ARSENAL_20260512/`.

## 2. Количество источников

**24 источника** проиндексированы с URL и reliability rating.

## 3. Top 10 tools to consider soon

1. **Rich** — colored Python CLI output (pip install rich)
2. **jq** — JSON processing в shell
3. **gitleaks** — secret scanning gate
4. **jsonschema** — receipt/schema validation
5. **check-jsonschema** — CLI schema validation
6. **difftastic** — structural code diff
7. **fd** — fast file search
8. **bat** — syntax-highlighted file view
9. **ripgrep** — already used, formalize
10. **7-Zip** — bundle handling (already installed)

## 4. Recommended SCRIPTORIUM minimal shape

- **НЕ новый орган** — registry-level подсистема
- **Файлы:** обновлённый `REGISTRY/SCRIPT_REGISTRY.json` (v0_2 schema) + `schemas/script_registry.schema.json` + `TOOLS/generate_script_index_v0_1.py`
- **Каждый скрипт:** path, owner_organ, platform, safety_class, status, example_invocation
- **Автогенерация:** скрипт сканирует filesystem и создаёт entries
- **Интеграция:** Servitor читает registry для discovery, Sanctum показывает в "Machinery" panel

## 5. Recommended ARSENAL minimal shape

- **НЕ новый орган** — Mechanicus reference library
- **Файлы:** `REGISTRY/ARSENAL_TOOL_INDEX.json` + `REGISTRY/ARSENAL_INSTALL_STATUS.json` + `schemas/arsenal_tool.schema.json`
- **Каждый tool:** name, category, platform, purpose, risk, install_now (yes/no/maybe), official_url
- **Workflow:** Owner reviews → approves → installs → verifies → marks installed
- **Priority tiers:** P0 (now) / P1 (after Arc 2) / P2 (future) / P3 (avoid)

## 6. Что реализовать первым

1. `TASK-20260513-SCRIPT-REGISTRY-V0_2` — обновить script registry, убрать UNKNOWN, добавить все скрипты
2. `TASK-20260513-ARSENAL-REGISTRY-V0_1` — создать tool catalog с 10 P0 candidates
3. `TASK-20260513-CLI-RICH-HELPER-V0_1` — Rich-based verdict output для всех scripts

## 7. Risks / do-not-install-yet

**НЕ устанавливать сейчас:**
- Ollama / local LLM — нет clear use case + resource policy
- Streamlit / web dashboard — Sanctum Qt = primary
- SQLite task database — JSON files достаточны
- Docker — VM2 проще
- Any auto-commit/auto-push tool — bypass Owner gate
- Temporal/Airflow — too heavy, inspiration only
- Cloud-dependent secret scanners — use local gitleaks

**Risks при установке:**
- Каждый `pip install` = новая dependency. Pin versions.
- Каждый binary tool = platform-specific. Track in ARSENAL_INSTALL_STATUS.
- Rich = optional dependency, not hard requirement. Scripts must work without it (fallback to plain print).

---

*Research pack завершён. Репозиторий не модифицирован. Все рекомендации = advisory. Owner решает что адаптировать.*
```