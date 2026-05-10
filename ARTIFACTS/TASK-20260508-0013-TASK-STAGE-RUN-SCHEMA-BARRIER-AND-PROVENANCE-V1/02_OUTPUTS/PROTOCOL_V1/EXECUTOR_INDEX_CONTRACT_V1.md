# EXECUTOR_INDEX_CONTRACT_V1

## Purpose
Define a strict executor registry contract used by scripts and barrier verification.

## Required fields
- executor_id
- producer_type
- contour_id
- executor_role
- authority_level_max
- allowed_actions
- forbidden_actions
- active
- notes

## Mandatory producer types
- PC_SERVITOR
- VM2_WORKER
- OWNER_MANUAL

## Future-safe but inactive producer types
- LOCAL_LLM_WORKER
- REMOTE_AGENT_WORKER
- SPECULUM_REVIEWER

## Forbidden for accepted bundles
- UNKNOWN

## Validation
1. producer_type UNKNOWN is always rejected at acceptance stage.
2. executor_id must be non-empty and stable.
3. contour_id and producer_type must be compatible.
4. VM2_WORKER authority_level_max cannot exceed STAGE_OUTPUT.
