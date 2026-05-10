# STAGE_SCHEMA_V1

## Purpose
Define a stage as the smallest parallel-safe execution unit inside one TASK_ID.

## Required fields
- task_id
- stage_id
- stage_name
- stage_goal
- contour_id
- expected_producer_type
- input_contract_ref
- output_contract_ref
- receipt_required
- provenance_required
- barrier_checkpoint_required
- stage_status
- notes

## Allowed values
contour_id:
- PC
- VM2
- OWNER_MANUAL

expected_producer_type:
- PC_SERVITOR
- VM2_WORKER
- OWNER_MANUAL

stage_status:
- DECLARED
- DISPATCHED
- RUNNING
- COMPLETED
- FAILED
- BLOCKED
- CONFLICT

## Validation
1. stage_id must be unique inside one task.
2. stage_id must map to exactly one contour for one run attempt.
3. output_contract_ref must include manifest, receipt, and provenance expectations.
4. barrier_checkpoint_required must be true for all execution stages.

## Rejection conditions
- stage without contour_id
- stage without expected_producer_type
- stage marked COMPLETED without receipt and provenance
