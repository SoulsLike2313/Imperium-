# Agent KPD Self-Review Contract V0.1

## Purpose

This contract makes every large agent run improve future IMPERIUM efficiency.

KPD means useful action density: how much real progress, reusable tooling, truth, and delivery capability was produced per unit of agent effort.

## Applies To

Required for:
- large reasoning agents;
- Codex/Kiro/Logos/Speculum-grade tasks;
- tasks that create tools;
- tasks that touch architecture;
- tasks that produce more than one report/contract/gate;
- agent-factory tasks;
- deliverable-factory tasks.

Optional for:
- tiny local executor tasks.

## Required Questions

At the end of a major task, the agent must answer:

1. What wasted time or tokens?
2. What instructions were too broad or unclear?
3. Which existing tools should have been reused?
4. Which tools had to be created because they did not exist?
5. Which generated tools must be preserved for review?
6. Which artifacts should go to Scriptorium absorption queue?
7. Which future narrow agent profile would have performed this task better?
8. Which context pack or reading route would improve the next run?
9. Which gate/checklist should prevent repeated mistakes?
10. What should be automated next?

## Required Output Shape

```json
{
  "agent_kpd_self_review": {
    "task_id": "",
    "agent_role": "",
    "useful_outputs": [],
    "waste_points": [],
    "missing_tools": [],
    "generated_tools_to_preserve": [],
    "recommended_script_absorption": [],
    "recommended_narrow_agent_profiles": [],
    "future_prompt_improvements": [],
    "future_gate_or_checklist_recommendations": [],
    "kpd_verdict": "GOOD / PARTIAL / WASTEFUL / BLOCKED"
  }
}
```

## KPD Verdicts

GOOD:
The task produced useful outputs, preserved tools, and improved future execution.

PARTIAL:
The task succeeded but had avoidable inefficiency or missing tools.

WASTEFUL:
The task consumed work without enough durable artifacts, or repeated known discovery.

BLOCKED:
The task could not proceed because required truth, gates, paths, or tools were missing.

## Forbidden Claims

Do not claim high KPD if:
- useful scripts were deleted;
- generated tools were not registered;
- the task required repeated manual rediscovery;
- reports were oversized;
- pass criteria were not self-assessed;
- future agent specialization was obvious but not recorded.

## Relation to Agent Factory

Every KPD review should feed future Agent Factory design.

Recommended agent profile discoveries must be added to future backlog when useful.
