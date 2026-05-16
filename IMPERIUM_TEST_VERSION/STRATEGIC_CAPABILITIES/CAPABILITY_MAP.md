# IMPERIUM STRATEGIC CAPABILITY MAP

**Version:** 1.0.0  
**Created:** 2026-05-16  
**Status:** FOUNDATION

---

## Overview

This document maps the six strategic capabilities that IMPERIUM must develop to become a local engineering OS capable of executing real freelance/product tasks.

---

## Capability Summary

| # | Capability | Status | Maturity |
|---|------------|--------|----------|
| 1 | Freelance Task Execution | SPEC_ONLY | Foundation |
| 2 | Presentation System | SPEC_ONLY | Foundation |
| 3 | Distributed Contours | SPEC_ONLY | Foundation |
| 4 | Second Brain Memory Zones | SPEC_ONLY | Foundation |
| 5 | CLI Agent Port | WORKING | MVP |
| 6 | Local LLM Port | HEALTH_CHECK_ONLY | Foundation |

---

## 1. Freelance Task Execution

**Purpose:** Accept external tasks/TZ and deliver working results.

**Target Corridor:**
```
External Task/TZ → Intake → Decomposition → Owner Questions → Plan → 
Execution Sandbox → Tests → Evidence Bundle → Delivery Package → 
Mini Presentation → Support/Patch Path
```

**Current Status:** SPEC_ONLY
- Specification defined
- Schema defined
- Sample synthetic TZ created
- Sample intake JSON created
- NOT executable yet

**Files:**
- `FREELANCE_EXECUTION/FREELANCE_TASK_CORRIDOR_SPEC.md`
- `FREELANCE_EXECUTION/freelance_task_corridor.schema.json`
- `FREELANCE_EXECUTION/SAMPLE_SYNTHETIC_TZ.md`
- `FREELANCE_EXECUTION/SAMPLE_TASK_INTAKE.json`

---

## 2. Presentation System

**Purpose:** Present IMPERIUM and its products to people/clients.

**Target Outputs:**
- Product presentation (slide-deck-like)
- Interactive summary/dashboard
- Capability map with proof/evidence links
- Strengths/weaknesses/risks analysis

**Current Status:** SPEC_ONLY
- Specification defined
- Schema defined
- Self-summary created (Russian for Owner)
- Self-summary JSON created
- NOT generating real presentations yet

**Files:**
- `PRESENTATION_SYSTEM/PRESENTATION_SYSTEM_SPEC.md`
- `PRESENTATION_SYSTEM/product_summary.schema.json`
- `PRESENTATION_SYSTEM/IMPERIUM_SELF_SUMMARY_RU.md`
- `PRESENTATION_SYSTEM/IMPERIUM_SELF_SUMMARY.json`

---

## 3. Distributed Contours

**Purpose:** Distribute tasks between PC and Ubuntu laptop via SSH.

**Contours:**
- PC Contour (main, Windows)
- Ubuntu Laptop Contour (secondary, Linux via SSH)

**Current Status:** SPEC_ONLY
- Specification defined
- Schema defined
- Profile templates created
- SSH capability check script created
- NOT verified (no credentials)

**Files:**
- `DISTRIBUTED_CONTOURS/DISTRIBUTED_CONTOURS_SPEC.md`
- `DISTRIBUTED_CONTOURS/contour_profile.schema.json`
- `DISTRIBUTED_CONTOURS/pc_contour_profile.template.json`
- `DISTRIBUTED_CONTOURS/ubuntu_laptop_contour_profile.template.json`
- `DISTRIBUTED_CONTOURS/ssh_capability_check.ps1`

**Manual Confirmation Required:**
- SSH connection to laptop
- Laptop environment discovery
- Task routing rules validation

---

## 4. Second Brain Memory Zones

**Purpose:** Selectable memory zones like Obsidian-style blocks.

**Features:**
- Multiple memory zones
- Metadata per zone (topic, scope, source, sensitivity, freshness, trust)
- Context pack export
- Agent can walk through memory zones

**Current Status:** SPEC_ONLY
- Specification defined
- Schemas defined
- Sample zones created (synthetic)
- Sample context pack created (synthetic)
- NOT connected to real data

**Files:**
- `SECOND_BRAIN/SECOND_BRAIN_MEMORY_ZONES_SPEC.md`
- `SECOND_BRAIN/memory_zone.schema.json`
- `SECOND_BRAIN/context_pack.schema.json`
- `SECOND_BRAIN/SAMPLE_MEMORY_ZONES.json`
- `SECOND_BRAIN/SAMPLE_CONTEXT_PACK.json`

**Manual Confirmation Required:**
- Real data ingestion
- Private data handling

---

## 5. CLI Agent Port

**Purpose:** CLI entry point for Servitor/Codex agent.

**Commands:**
- `--mode health` — Health check
- `--mode summarize --input <file>` — Summarize input
- `--mode inspect-capabilities` — List capabilities

**Current Status:** WORKING
- Specification defined
- Schemas defined
- CLI script implemented
- Commands work locally
- NOT connected to real agent

**Files:**
- `CLI_AGENT_PORT/CLI_AGENT_PORT_SPEC.md`
- `CLI_AGENT_PORT/cli_agent_request.schema.json`
- `CLI_AGENT_PORT/cli_agent_response.schema.json`
- `CLI_AGENT_PORT/imperium_cli_agent_port.py`
- `CLI_AGENT_PORT/sample_request.json`

---

## 6. Local LLM Port

**Purpose:** Connect local LLMs for inference.

**Features:**
- Model capability profiles
- Context-size limits
- Safe task routing
- Health check

**Current Status:** HEALTH_CHECK_ONLY
- Specification defined
- Schemas defined
- Config template created
- Health check script implemented
- Reports NOT_CONFIGURED/NOT_INSTALLED honestly
- NOT connected to real model

**Files:**
- `LOCAL_LLM_PORT/LOCAL_LLM_PORT_SPEC.md`
- `LOCAL_LLM_PORT/local_llm_profile.schema.json`
- `LOCAL_LLM_PORT/local_llm_request.schema.json`
- `LOCAL_LLM_PORT/local_llm_response.schema.json`
- `LOCAL_LLM_PORT/local_llm_config.template.json`
- `LOCAL_LLM_PORT/local_llm_health_check.py`

**Manual Confirmation Required:**
- Model installation
- Model configuration
- Inference testing

---

## Maturity Levels

| Level | Meaning |
|-------|---------|
| FOUNDATION | Spec and schemas only |
| HEALTH_CHECK_ONLY | Can report status, no real function |
| MVP | Minimal working implementation |
| WORKING | Functional for intended purpose |
| PRODUCTION | Ready for real use |

---

## Next Steps

1. **CLI Agent Port** — Connect to real agent (Codex/Servitor)
2. **Local LLM Port** — Install and configure local model
3. **Distributed Contours** — Test SSH connection to laptop
4. **Second Brain** — Ingest real memory data
5. **Freelance Execution** — Build executable pipeline
6. **Presentation System** — Generate real presentations

---

## Evidence

All capability files are in `IMPERIUM_TEST_VERSION/STRATEGIC_CAPABILITIES/`.
Verification script: `TOOLS/check_strategic_capability_foundation.py`
