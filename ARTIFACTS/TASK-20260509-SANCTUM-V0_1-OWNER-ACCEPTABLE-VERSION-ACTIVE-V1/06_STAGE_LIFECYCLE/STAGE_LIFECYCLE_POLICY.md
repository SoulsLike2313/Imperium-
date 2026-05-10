# Stage Lifecycle Policy

{
  "schema_version": "STAGE_LIFECYCLE_POLICY_V1",
  "task_id": "TASK-20260509-SANCTUM-V0_1-OWNER-ACCEPTABLE-VERSION-ACTIVE-V1",
  "required_for_each_stage": [
    "STAGE_START_RECEIPT",
    "files_read",
    "files_written",
    "bugs_found",
    "fixes_made",
    "validation_result",
    "STAGE_END_RECEIPT or STAGE_BLOCKED_RECEIPT"
  ],
  "stage_loop": [
    "start_stage",
    "do_scoped_work",
    "record_changed_files",
    "run_validation",
    "if_pass_write_end_receipt",
    "if_safe_fail_repair_and_rerun",
    "if_semantic_or_destructive_stop_for_owner"
  ],
  "owner_approval_required_for": [
    "delete",
    "move",
    "canon migration",
    "VM2 activation",
    "THRONE contact",
    "E2E activation",
    "watchers",
    "background automation",
    "scope change",
    "baseline acceptance"
  ]
}