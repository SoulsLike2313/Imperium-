# V1 Known Failures and Preventions

| risk_id | likely_failure | early_signal | prevention | fallback_or_stop_behavior | affected_stage_group | source |
|---|---|---|---|---|---|---|
| RISK-001 | schema churn | repeated schema edits across adjacent stages | freeze minimum schema set first | stop and re-sequence schema-first lane | LT-01 LT-02 | Kiro |
| RISK-002 | dashboard before backend truth | dashboard panel without report path | enforce dashboard truth gate | block UI stage until adapters and reports exist | LT-04 LT-05 | Kiro+Speculum |
| RISK-003 | mock data leak | synthetic numbers without provenance | require evidence index per panel | mark panel unknown and block green state | LT-04 LT-05 | Speculum |
| RISK-004 | stale report shown green | missing expires_after_seconds | stale status model required | force stale badge and non-green verdict | LT-04 LT-06 | Speculum |
| RISK-005 | action button without receipt | action event has no receipt artifact | action contract with required receipt schema | disable action and emit blocker | LT-05 | Speculum+Owner |
| RISK-006 | Astronomicon/Admin state collision | scope or stage truth modified by wrong owner | ownership matrix gate | stop and split ownership scope | LT-02 LT-03 | Speculum |
| RISK-007 | Officio/Admin assignment collision | role assignment and execution state diverge | role contract and route sheet linkage | block stage and require reconciliation receipt | LT-03 | Speculum |
| RISK-008 | Doctrinarium stale law gate | gate verdict without fresh law report | stale-aware law gate checks | block task start corridor | LT-02 LT-03 | Speculum |
| RISK-009 | disabled inquisition fake active | hook displayed as sent | explicit disabled hook contract | hard fail no-fake-green gate | LT-02 LT-06 | Speculum |
| RISK-010 | Sanctum source-of-truth overreach | Sanctum data differs from source reports | read-only aggregation contract | stop Sanctum stage and rebind sources | LT-06 | Speculum |
| RISK-011 | repo pollution | unrelated runtime artifacts in diff | repo purity gate every local task | halt and isolate canonical scope | all | Speculum |
| RISK-012 | 40-stage chaos | stage count growth without budget control | decomposition budget thresholds | stop and replan with owner gate | planning | Kiro+Speculum |
| RISK-013 | one impossible giant stage | stage contains multiple owner domains and schema+impl | stage composition constraints | split stage before execution | planning | Speculum |
| RISK-014 | hidden owner gate | local task closes without owner checkpoint | mandatory owner gate after each local task | stop launch continuation | all local task boundaries | Owner |
| RISK-015 | VM2 assumed for commit path | scripts reference VM2 commit flow | LAW-001 and vm2 boundary gate | block and record violation | all | Owner+Doctrinarium |
| RISK-016 | mojibake or encoding regression | parse failures or broken glyph output | UTF-8/mojibake gate | fail stage and rewrite artifact | all | Owner+Speculum |
| RISK-017 | hidden warnings behind PASS | warning-producing checks marked PASS without warnings list | no-fake-green rule for PASS_WITH_WARNINGS | fail stage report quality gate | all | Speculum |
| RISK-018 | final bundle missing evidence | bundle manifest lacks required receipts | final bundle manifest contract | block certification closure | LT-06 LT-07 | Kiro+Speculum |
