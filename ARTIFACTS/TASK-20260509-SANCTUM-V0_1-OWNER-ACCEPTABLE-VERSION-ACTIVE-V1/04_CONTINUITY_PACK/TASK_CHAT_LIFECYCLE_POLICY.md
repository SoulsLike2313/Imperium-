# Task Chat Lifecycle Policy

{
  "schema_version": "TASK_CHAT_LIFECYCLE_POLICY_V1",
  "task_id": "TASK-20260509-SANCTUM-V0_1-OWNER-ACCEPTABLE-VERSION-ACTIVE-V1",
  "one_major_task_one_logos_prime_chat": true,
  "one_major_task_one_servitor_chat": true,
  "on_task_start": "Create start continuity pack.",
  "during_task": "Update active snapshot, receipts, stage ledger, artifacts.",
  "on_mega_pass": [
    "Create final task report.",
    "Create final continuity pack.",
    "Notify Owner to open new Logos-Prime chat.",
    "Notify Owner to open new Servitor chat.",
    "Do not continue architecture drift in closed task chat."
  ],
  "mega_pass_definition": [
    "Owner accepts result or candidate status.",
    "All required artifacts exist.",
    "Validation is clean or known warnings are explicitly accepted.",
    "Speculum review handled if required.",
    "Next task or next chat handoff is defined."
  ]
}