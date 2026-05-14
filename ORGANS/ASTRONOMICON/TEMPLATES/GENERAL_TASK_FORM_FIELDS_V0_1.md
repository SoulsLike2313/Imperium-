# GENERAL TASK FORM FIELDS V0.1

| UI field | YAML/Markdown target | required? | widget type | validation | notes |
|---|---|---|---|---|---|
| General Task ID | `yaml.general_task_id` | yes | text input | non-empty, `GT-` recommended prefix | immutable after save in MVP |
| Title | `yaml.title` | yes | text input | non-empty | short owner-facing label |
| Owner Goal | `yaml.owner_goal` | yes | textarea | non-empty | single source of intent |
| Desired Outcome | `yaml.desired_outcome` | yes | textarea | non-empty | measurable result preferred |
| Scope In | `yaml.scope_in[]` | yes | multiline list | at least 1 item | zones/files allowed |
| Scope Out | `yaml.scope_out[]` | yes | multiline list | at least 1 item | explicit exclusions |
| Constraints | `yaml.constraints[]` | yes | multiline list | at least 1 item | hard execution limits |
| Forbidden Actions | `yaml.forbidden_actions[]` | yes | multiline list | at least 1 item | no-go operations |
| Known Context | `yaml.known_context[]` | yes | multiline list | at least 1 item | verified truths |
| Unknowns | `yaml.unknowns[]` | yes | multiline list | at least 1 item | open questions |
| Success Criteria | `yaml.success_criteria[]` | yes | multiline list | at least 1 item | acceptance |
| Failure Criteria | `yaml.failure_criteria[]` | yes | multiline list | at least 1 item | fail-closed triggers |
| Expected Deliverables | `yaml.expected_deliverables[]` | yes | multiline list | at least 1 item | outputs and artifacts |
| Target Organs | `yaml.target_organs[]` | yes | multi-select/list | at least 1 item | organ ownership |
| Risk Level | `yaml.risk_level` | yes | select | LOW/MEDIUM/HIGH/CRITICAL | coarse risk |
| Owner Approval Points | `yaml.owner_approval_points[]` | yes | multiline list | at least 1 item | explicit gates |
| Decomposition Hints | `yaml.decomposition_hints[]` | yes | multiline list | at least 1 item | candidate split hints |
| Local Candidate Count Hint | `yaml.local_task_candidate_count_hint` | yes | number input | integer >= 1 | decomposition baseline |
| Priority | `yaml.priority` | yes | select | LOW/MEDIUM/HIGH/CRITICAL | sequencing hint |
| Dependencies | `yaml.dependencies[]` | yes | multiline list | at least 1 item (or `none`) | upstream requirements |
| Local/Private Boundary Notes | `yaml.local_private_boundary_notes[]` | yes | multiline list | at least 1 item | context placement guard |
| Dashboard Display Title | `yaml.dashboard_display_title` | yes | text input | non-empty | compact card title |
| Tags | `yaml.tags[]` | yes | tag input | at least 1 item | filtering/grouping |
| Created By | `yaml.created_by` | yes | text input | non-empty | actor identity |
| Created At | `yaml.created_at` | yes | text input | ISO-8601 string | provenance |
| Current Status | `yaml.current_status` | yes | select | DRAFT/UNDER_REVIEW/APPROVED/REJECTED | workflow state |
| Background | `markdown: ## Background` | yes | textarea | non-empty | narrative context |
| Detailed Owner Intent | `markdown: ## Detailed Owner Intent` | yes | textarea | non-empty | practical intent detail |
| Known Context (narrative) | `markdown: ## Known Context` | yes | textarea | non-empty | human-readable context |
| Unknowns and Questions | `markdown: ## Unknowns and Questions` | yes | textarea | non-empty | uncertainty map |
| Notes for Decomposition | `markdown: ## Notes for Decomposition` | yes | textarea | non-empty | split guidance |
| Notes for Speculum | `markdown: ## Notes for Speculum` | yes | textarea | non-empty | strict review asks |
| Notes for Dashboard Display | `markdown: ## Notes for Dashboard Display` | yes | textarea | non-empty | panel text |
