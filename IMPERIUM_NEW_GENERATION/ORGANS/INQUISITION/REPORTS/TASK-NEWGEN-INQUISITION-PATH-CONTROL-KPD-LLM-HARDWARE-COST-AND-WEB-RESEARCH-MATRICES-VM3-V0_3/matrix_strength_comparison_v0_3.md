# Matrix Strength Comparison V0_3

## Earlier Matrix Behavior

Earlier candidate matrices were strong at preventing fake PASS claims but weak at pricing the work. They asked for evidence levels, caps, and red-team checks, but they did not force the agent to separate LLM context cost, output bloat, retries, web-search cost, local hardware cost, local organ-agent cost, Owner manual effort, artifact retention cost, and Throne fallback value.

## V0_3 Improvements

- Local verdict is separated from global carried caps.
- Fake economy is explicitly defined as FAIL when evidence is removed.
- Hardware and local-agent metrics include `UNKNOWN_NOT_INSTRUMENTED` instead of invented numbers.
- Web research source quality has a schema and a receipt.
- KPD includes value, evidence strength, context reduction, output reduction without evidence loss, manual-work reduction, and future friction reduction.
- Validator seed checks required outputs, source coverage, examples, and fake-economy traps.

## Remaining Weaknesses

- The validator is seed-level and not yet a canon Mechanicus tool.
- Task-wide CPU/memory/disk instrumentation is proposed but not fully automatic.
- Provider token and cache metrics require real API usage metadata, unavailable in this local artifact-only task.
- Independent external review is still required before any clean campaign-level PASS.
