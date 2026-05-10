# BUNDLE_PROVENANCE_SCHEMA_V1

## Required fields
- task_id
- stage_id
- run_id
- contour_id
- producer_type
- producer_id
- executor_role
- creation_mode
- created_at_utc
- produced_on_host_class
- source_bundle_name
- source_bundle_sha256
- parent_bundle_refs
- transfer_method
- transfer_actor
- manual_touchpoints
- authority_level
- acceptance_scope
- verification_status

## Allowed values
contour_id:
- PC
- VM2
- OWNER_MANUAL

producer_type:
- PC_SERVITOR
- VM2_WORKER
- OWNER_MANUAL

creation_mode:
- SCRIPTED
- MANUAL
- SEMI_MANUAL

transfer_method:
- LOCAL_CREATE
- SSH_SEND
- SSH_FETCH
- MANUAL_COPY
- MANUAL_UPLOAD
- NONE

authority_level:
- WORKING_ARTIFACT
- STAGE_OUTPUT
- FETCHED_STAGE_BUNDLE
- VERIFIED_STAGE_BUNDLE
- FINAL_TASK_BUNDLE
- REVIEW_REQUEST
- BLOCKED_ARTIFACT

verification_status:
- UNVERIFIED
- HASH_VERIFIED
- MANIFEST_VERIFIED
- RECEIPT_VERIFIED
- BARRIER_PASSED
- BARRIER_FAILED
- REJECTED

## Mandatory rules
1. provenance is mandatory for all accepted artifacts.
2. producer_type UNKNOWN is forbidden for acceptance.
3. OWNER_MANUAL artifacts must declare creation_mode MANUAL or SEMI_MANUAL.
4. VM2 artifact cannot declare authority_level FINAL_TASK_BUNDLE.
