# Performance Optimization Plan Next Step Map V0.1

## What Was Learned
- Route/API truth is valid, FPS truth is valid, and FPS remains blocked.
- File asset weight is not primary blocker; CSS/JS/effect pressure is likely primary.

## Next 3 Tasks
1. `TASK-SECOND-BRAIN-V07-PERFORMANCE-OPTIMIZATION-SLICE-1-MOTION-THROTTLE-V0_1`
2. `TASK-SECOND-BRAIN-V07-PERFORMANCE-OPTIMIZATION-SLICE-2-CSS-EFFECT-REDUCTION-V0_1`
3. `TASK-SECOND-BRAIN-V07-PERFORMANCE-REBASELINE-AND-BUDGET-RECHECK-V0_1`

## Recommended Immediate Next Task
- `TASK-SECOND-BRAIN-V07-PERFORMANCE-OPTIMIZATION-SLICE-1-MOTION-THROTTLE-V0_1`
- why: Motion/throttle is the safest first reversible slice to reduce frame pressure before deeper CSS/JS surgery.

## Post-Implementation Verification
- Route/API truth gates remain PASS.
- FPS metrics improve toward acceptance.
- No truth overlay break and no visual identity collapse.

## Visual Construction Resume Rule
- Visual construction can resume only after FPS acceptance criteria pass with truth gates intact.
