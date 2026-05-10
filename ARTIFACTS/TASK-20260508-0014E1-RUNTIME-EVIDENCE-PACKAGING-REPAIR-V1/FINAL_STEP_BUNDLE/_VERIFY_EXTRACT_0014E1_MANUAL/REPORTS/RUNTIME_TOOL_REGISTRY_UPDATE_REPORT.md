# RUNTIME_TOOL_REGISTRY_UPDATE_REPORT

{
  "task_id": "TASK-20260508-0014E-STAGE-COORDINATION-RUNTIME-MINIMAL-IMPLEMENTATION-V1",
  "status": "ACTIVE_LOCAL_DRYRUN_ONLY",
  "blocked": "BLOCKED_FOR_VM2_UNTIL_0014F_0014G_PASS",
  "tools": [
    {
      "tool_id": "IDENTITY_VALIDATE",
      "path": "15_STAGE_COORDINATION/identity_validate.py",
      "sha256": "3ec7b38bf80f0002fd5ebec7b872a7ca8343ff52157aeb6a4dc471fa8bbab304",
      "status": "ACTIVE_LOCAL_DRYRUN_ONLY",
      "writes_receipt": true,
      "writes_ledger_event": false,
      "writes_owner_report": true,
      "writes_provenance": false,
      "blocked_actions": [
        "vm2_contact",
        "real_e2e",
        "throne_transfer",
        "watchers",
        "latest_logic"
      ],
      "local_test_receipt_ref": "REPORTS/0014E_LOCAL_TEST_REPORT.md"
    },
    {
      "tool_id": "ARTIFACT_MANIFEST_WRITE",
      "path": "15_STAGE_COORDINATION/artifact_manifest_write.py",
      "sha256": "d3b8d40072c82b66958c88fff0ff85ee32b2a8973c4d476f8048ef14f9ae2731",
      "status": "ACTIVE_LOCAL_DRYRUN_ONLY",
      "writes_receipt": true,
      "writes_ledger_event": false,
      "writes_owner_report": true,
      "writes_provenance": true,
      "blocked_actions": [
        "vm2_contact",
        "real_e2e",
        "throne_transfer",
        "watchers",
        "latest_logic"
      ],
      "local_test_receipt_ref": "REPORTS/0014E_LOCAL_TEST_REPORT.md"
    },
    {
      "tool_id": "ARTIFACT_MANIFEST_VERIFY",
      "path": "15_STAGE_COORDINATION/artifact_manifest_verify.py",
      "sha256": "05f6b839aa8f0f27c6eb9f22bd0af1f6473e9bd807f5d61c66f7fa83d440f582",
      "status": "ACTIVE_LOCAL_DRYRUN_ONLY",
      "writes_receipt": true,
      "writes_ledger_event": false,
      "writes_owner_report": true,
      "writes_provenance": false,
      "blocked_actions": [
        "vm2_contact",
        "real_e2e",
        "throne_transfer",
        "watchers",
        "latest_logic"
      ],
      "local_test_receipt_ref": "REPORTS/0014E_LOCAL_TEST_REPORT.md"
    },
    {
      "tool_id": "LEDGER_APPEND",
      "path": "15_STAGE_COORDINATION/ledger_append.py",
      "sha256": "8c7a9515cd0e5e50ed79fe94595a2134ffe91eb27f10a829426e0df725869dab",
      "status": "ACTIVE_LOCAL_DRYRUN_ONLY",
      "writes_receipt": true,
      "writes_ledger_event": true,
      "writes_owner_report": true,
      "writes_provenance": false,
      "blocked_actions": [
        "vm2_contact",
        "real_e2e",
        "throne_transfer",
        "watchers",
        "latest_logic"
      ],
      "local_test_receipt_ref": "REPORTS/0014E_LOCAL_TEST_REPORT.md"
    },
    {
      "tool_id": "LEDGER_REPLAY_VERIFY",
      "path": "15_STAGE_COORDINATION/ledger_replay_verify.py",
      "sha256": "057c1a488c1088395ddd2a8435af733d58f6447eccf73360464e7fac0fd28252",
      "status": "ACTIVE_LOCAL_DRYRUN_ONLY",
      "writes_receipt": true,
      "writes_ledger_event": false,
      "writes_owner_report": true,
      "writes_provenance": false,
      "blocked_actions": [
        "vm2_contact",
        "real_e2e",
        "throne_transfer",
        "watchers",
        "latest_logic"
      ],
      "local_test_receipt_ref": "REPORTS/0014E_LOCAL_TEST_REPORT.md"
    },
    {
      "tool_id": "STAGE_SIGNAL_EMIT",
      "path": "15_STAGE_COORDINATION/stage_signal_emit.py",
      "sha256": "a7ab1c9f7fd7b49c28af3ffb3e29c2c2452540608d2a0ae191c72c512259ba37",
      "status": "ACTIVE_LOCAL_DRYRUN_ONLY",
      "writes_receipt": true,
      "writes_ledger_event": true,
      "writes_owner_report": true,
      "writes_provenance": true,
      "blocked_actions": [
        "vm2_contact",
        "real_e2e",
        "throne_transfer",
        "watchers",
        "latest_logic"
      ],
      "local_test_receipt_ref": "REPORTS/0014E_LOCAL_TEST_REPORT.md"
    },
    {
      "tool_id": "STAGE_SIGNAL_ACK",
      "path": "15_STAGE_COORDINATION/stage_signal_ack.py",
      "sha256": "cea7502e9b48b013c93092dd3762f307062667b7340282a1f3a7ca9b81761f2b",
      "status": "ACTIVE_LOCAL_DRYRUN_ONLY",
      "writes_receipt": true,
      "writes_ledger_event": true,
      "writes_owner_report": true,
      "writes_provenance": false,
      "blocked_actions": [
        "vm2_contact",
        "real_e2e",
        "throne_transfer",
        "watchers",
        "latest_logic"
      ],
      "local_test_receipt_ref": "REPORTS/0014E_LOCAL_TEST_REPORT.md"
    },
    {
      "tool_id": "STAGE_SIGNAL_VERIFY",
      "path": "15_STAGE_COORDINATION/stage_signal_verify.py",
      "sha256": "fdcef7b952a1868350cf0c81af23cbf206a254568facef4095488460b763377d",
      "status": "ACTIVE_LOCAL_DRYRUN_ONLY",
      "writes_receipt": true,
      "writes_ledger_event": false,
      "writes_owner_report": true,
      "writes_provenance": false,
      "blocked_actions": [
        "vm2_contact",
        "real_e2e",
        "throne_transfer",
        "watchers",
        "latest_logic"
      ],
      "local_test_receipt_ref": "REPORTS/0014E_LOCAL_TEST_REPORT.md"
    },
    {
      "tool_id": "STAGE_GATE_DECIDE",
      "path": "15_STAGE_COORDINATION/stage_gate_decide.py",
      "sha256": "956f7c048ed3276914d22e1b641c5ff0965b82cde485e188ef2b4825859609f4",
      "status": "ACTIVE_LOCAL_DRYRUN_ONLY",
      "writes_receipt": true,
      "writes_ledger_event": true,
      "writes_owner_report": true,
      "writes_provenance": false,
      "blocked_actions": [
        "vm2_contact",
        "real_e2e",
        "throne_transfer",
        "watchers",
        "latest_logic"
      ],
      "local_test_receipt_ref": "REPORTS/0014E_LOCAL_TEST_REPORT.md"
    },
    {
      "tool_id": "STAGE_WAIT_FOR_SIGNAL",
      "path": "15_STAGE_COORDINATION/stage_wait_for_signal.py",
      "sha256": "6427c3f1d0d777486e4cc9d81129c7d972e7792d1ff05b07af5628fc16274e7b",
      "status": "ACTIVE_LOCAL_DRYRUN_ONLY",
      "writes_receipt": true,
      "writes_ledger_event": true,
      "writes_owner_report": true,
      "writes_provenance": false,
      "blocked_actions": [
        "vm2_contact",
        "real_e2e",
        "throne_transfer",
        "watchers",
        "latest_logic"
      ],
      "local_test_receipt_ref": "REPORTS/0014E_LOCAL_TEST_REPORT.md"
    },
    {
      "tool_id": "STAGE_STOP_WITH_REASON",
      "path": "15_STAGE_COORDINATION/stage_stop_with_reason.py",
      "sha256": "87d23c1b8cede6526b421617efc76471bc397b8fb8b693fdd2ffcc1912903d33",
      "status": "ACTIVE_LOCAL_DRYRUN_ONLY",
      "writes_receipt": true,
      "writes_ledger_event": true,
      "writes_owner_report": true,
      "writes_provenance": false,
      "blocked_actions": [
        "vm2_contact",
        "real_e2e",
        "throne_transfer",
        "watchers",
        "latest_logic"
      ],
      "local_test_receipt_ref": "REPORTS/0014E_LOCAL_TEST_REPORT.md"
    },
    {
      "tool_id": "STAGE_COORDINATION_VIEW",
      "path": "15_STAGE_COORDINATION/stage_coordination_view.py",
      "sha256": "43b6c03aa7498bb427b308cf631024ee8b49efed6855b8c563dde19921d8b1e9",
      "status": "ACTIVE_LOCAL_DRYRUN_ONLY",
      "writes_receipt": true,
      "writes_ledger_event": false,
      "writes_owner_report": true,
      "writes_provenance": false,
      "blocked_actions": [
        "vm2_contact",
        "real_e2e",
        "throne_transfer",
        "watchers",
        "latest_logic"
      ],
      "local_test_receipt_ref": "REPORTS/0014E_LOCAL_TEST_REPORT.md"
    },
    {
      "tool_id": "STAGE_REPAIR_REQUEST",
      "path": "15_STAGE_COORDINATION/stage_repair_request.py",
      "sha256": "fca5c8e7d3415121b46c9a0e2167f53fcca62b773f341a8a4086b8845218e4c3",
      "status": "ACTIVE_LOCAL_DRYRUN_ONLY",
      "writes_receipt": true,
      "writes_ledger_event": true,
      "writes_owner_report": true,
      "writes_provenance": false,
      "blocked_actions": [
        "vm2_contact",
        "real_e2e",
        "throne_transfer",
        "watchers",
        "latest_logic"
      ],
      "local_test_receipt_ref": "REPORTS/0014E_LOCAL_TEST_REPORT.md"
    },
    {
      "tool_id": "INQUISITION_TRACE_AUDIT",
      "path": "15_STAGE_COORDINATION/inquisition_trace_audit.py",
      "sha256": "cba43b70f448ea8ab559484f41260b2fa5d6bd5e1daee957e734264a3bdb1f23",
      "status": "ACTIVE_LOCAL_DRYRUN_ONLY",
      "writes_receipt": true,
      "writes_ledger_event": false,
      "writes_owner_report": true,
      "writes_provenance": false,
      "blocked_actions": [
        "vm2_contact",
        "real_e2e",
        "throne_transfer",
        "watchers",
        "latest_logic"
      ],
      "local_test_receipt_ref": "REPORTS/0014E_LOCAL_TEST_REPORT.md"
    }
  ]
}
