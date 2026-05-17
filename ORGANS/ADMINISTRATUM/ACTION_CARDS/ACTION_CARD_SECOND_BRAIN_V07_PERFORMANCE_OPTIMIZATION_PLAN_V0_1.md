# ACTION CARD — Second Brain V0.7 Performance Optimization Plan V0.1

| Поле | Значение |
|---|---|
| Task name | TASK-SECOND-BRAIN-V07-PERFORMANCE-OPTIMIZATION-PLAN-V0_1 |
| Current HEAD | `fc0c094ef785a9879cf3e08c61a2d0dc09a88107` |
| Что запланировано | Срезовый, обратимый, измеримый план оптимизации FPS без ломки route/API/observability truth |
| Likely pressure zones | CSS эффекты (keyframes/animations/shadows/gradients), JS frame-loop и DOM churn |
| First implementation slice | `TASK-SECOND-BRAIN-V07-PERFORMANCE-OPTIMIZATION-SLICE-1-MOTION-THROTTLE-V0_1` |
| Acceptance targets | avg FPS >=50 (target 55), 1% low >=35 (target 45), route/API truth gates PASS |
| Что намеренно не изменялось | V0.6/V0.7 source, runtime/backend, runners/tools, visuals (implementation), optimization code |
| Exact report paths | `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/PERFORMANCE_OPTIMIZATION_PLAN_V0_1.json`; `...SLICE_PLAN...`; `...ACCEPTANCE_CRITERIA...`; `...RISK_REGISTER...`; `ORGANS/ASTRONOMICON/ROADMAPS/PERFORMANCE_OPTIMIZATION_PLAN_NEXT_STEP_MAP_V0_1.json` |
| Next allowed task | `TASK-SECOND-BRAIN-V07-PERFORMANCE-OPTIMIZATION-SLICE-1-MOTION-THROTTLE-V0_1` |
| Stop warnings | Стоп при route/API regression, visual identity collapse, fake-FPS gain, truth overlay break |
