window.DASHBOARD_BUNDLE = {
  "state": {
    "organ_id": "ADMINISTRATUM",
    "organ_name": "Administratum",
    "status": "PASS_WITH_WARNINGS",
    "generated_at_utc": "2026-05-15T06:29:01Z",
    "git_head": "fde9e511c8e1820a9986554633764660f79ac7e0",
    "checked_at_utc": "2026-05-15T06:29:01Z",
    "expires_after_seconds": 86400,
    "stale_status": "fresh",
    "warnings": [
      "owner_gated_mutating_actions_disabled"
    ],
    "blockers": [],
    "evidence_paths": [
      "ORGANS/ADMINISTRATUM/REPORTS/V1/action_read_receipt_v1.json",
      "ORGANS/ADMINISTRATUM/REPORTS/V1/action_refresh_receipt_v1.json",
      "ORGANS/ADMINISTRATUM/REPORTS/V1/action_write_blocked_receipt_v1.json",
      "ORGANS/ADMINISTRATUM/REPORTS/V1/admin_stage_completion_receipt_v1.json",
      "ORGANS/ADMINISTRATUM/REPORTS/V1/dashboard_render_report_v1.json",
      "ORGANS/ADMINISTRATUM/REPORTS/V1/organ_self_report_v1.json",
      "ORGANS/ADMINISTRATUM/REPORTS/V1/rollback_stop_receipt_v1.json",
      "ORGANS/ADMINISTRATUM/REPORTS/V1/route_work_packet_wiring_report_v1.json"
    ],
    "data_source_paths": [
      "ORGANS/ADMINISTRATUM/REPORTS/V1/action_read_receipt_v1.json",
      "ORGANS/ADMINISTRATUM/REPORTS/V1/action_refresh_receipt_v1.json",
      "ORGANS/ADMINISTRATUM/REPORTS/V1/action_write_blocked_receipt_v1.json",
      "ORGANS/ADMINISTRATUM/REPORTS/V1/admin_stage_completion_receipt_v1.json",
      "ORGANS/ADMINISTRATUM/REPORTS/V1/dashboard_render_report_v1.json",
      "ORGANS/ADMINISTRATUM/REPORTS/V1/organ_self_report_v1.json",
      "ORGANS/ADMINISTRATUM/REPORTS/V1/rollback_stop_receipt_v1.json",
      "ORGANS/ADMINISTRATUM/REPORTS/V1/route_work_packet_wiring_report_v1.json",
      "ORGANS/ADMINISTRATUM/REPORTS/V1/stage_completion_path_report_v1.json",
      "ORGANS/ADMINISTRATUM/REPORTS/V1/warning_acceptance_receipt_v1.json"
    ]
  },
  "metrics": {
    "organ_id": "ADMINISTRATUM",
    "generated_at_utc": "2026-05-15T06:29:01Z",
    "git_head": "fde9e511c8e1820a9986554633764660f79ac7e0",
    "metrics": {
      "report_count": 10,
      "warnings_count": 1,
      "blockers_count": 0,
      "evidence_count": 8,
      "stage_contracts_ready": 20,
      "organ_priority_index": 2
    }
  },
  "evidence": {
    "organ_id": "ADMINISTRATUM",
    "generated_at_utc": "2026-05-15T06:29:01Z",
    "git_head": "fde9e511c8e1820a9986554633764660f79ac7e0",
    "evidence_items": [
      {
        "kind": "report",
        "path": "ORGANS/ADMINISTRATUM/REPORTS/V1/action_read_receipt_v1.json"
      },
      {
        "kind": "report",
        "path": "ORGANS/ADMINISTRATUM/REPORTS/V1/action_refresh_receipt_v1.json"
      },
      {
        "kind": "report",
        "path": "ORGANS/ADMINISTRATUM/REPORTS/V1/action_write_blocked_receipt_v1.json"
      },
      {
        "kind": "report",
        "path": "ORGANS/ADMINISTRATUM/REPORTS/V1/admin_stage_completion_receipt_v1.json"
      },
      {
        "kind": "report",
        "path": "ORGANS/ADMINISTRATUM/REPORTS/V1/dashboard_render_report_v1.json"
      },
      {
        "kind": "report",
        "path": "ORGANS/ADMINISTRATUM/REPORTS/V1/organ_self_report_v1.json"
      },
      {
        "kind": "report",
        "path": "ORGANS/ADMINISTRATUM/REPORTS/V1/rollback_stop_receipt_v1.json"
      },
      {
        "kind": "report",
        "path": "ORGANS/ADMINISTRATUM/REPORTS/V1/route_work_packet_wiring_report_v1.json"
      },
      {
        "kind": "report",
        "path": "ORGANS/ADMINISTRATUM/REPORTS/V1/stage_completion_path_report_v1.json"
      },
      {
        "kind": "report",
        "path": "ORGANS/ADMINISTRATUM/REPORTS/V1/warning_acceptance_receipt_v1.json"
      }
    ]
  },
  "actions": {
    "organ_id": "ADMINISTRATUM",
    "generated_at_utc": "2026-05-15T06:29:01Z",
    "actions": [
      {
        "action_id": "administratum_open_dashboard_data",
        "action_type": "read_only_view",
        "enabled": true,
        "disabled_reason": "",
        "owner_gate_required": false,
        "expected_receipt_path": "ORGANS/ADMINISTRATUM/REPORTS/V1/action_read_receipt_v1.json",
        "failure_behavior": "show_error_and_keep_state"
      },
      {
        "action_id": "administratum_refresh_snapshot",
        "action_type": "read_only_export",
        "enabled": true,
        "disabled_reason": "",
        "owner_gate_required": false,
        "expected_receipt_path": "ORGANS/ADMINISTRATUM/REPORTS/V1/action_refresh_receipt_v1.json",
        "failure_behavior": "show_error_and_keep_previous_snapshot"
      },
      {
        "action_id": "administratum_write_state_transition",
        "action_type": "state_transition",
        "enabled": false,
        "disabled_reason": "owner_gate_required",
        "owner_gate_required": true,
        "expected_receipt_path": "ORGANS/ADMINISTRATUM/REPORTS/V1/action_write_blocked_receipt_v1.json",
        "failure_behavior": "blocked_no_mutation"
      }
    ]
  },
  "labels": {
    "en": {
      "status": "Status",
      "freshness": "Freshness",
      "generated": "Generated",
      "git": "Git Head",
      "metrics": "Metrics",
      "metric": "Metric",
      "value": "Value",
      "evidence": "Evidence",
      "actions": "Actions",
      "action": "Action",
      "mode": "Mode",
      "receipt": "Receipt",
      "enabled": "Enabled",
      "disabled": "Disabled",
      "sources": "Source paths"
    },
    "ru": {
      "status": "Статус",
      "freshness": "Свежесть",
      "generated": "Сформировано",
      "git": "Git Head",
      "metrics": "Метрики",
      "metric": "Метрика",
      "value": "Значение",
      "evidence": "Доказательства",
      "actions": "Действия",
      "action": "Действие",
      "mode": "Режим",
      "receipt": "Квитанция",
      "enabled": "Включено",
      "disabled": "Отключено",
      "sources": "Пути источников"
    }
  }
};
