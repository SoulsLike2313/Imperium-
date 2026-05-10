# ADMINISTRATUM PROMPT INTAKE SCHEMA V1

Required fields:
- task_id
- owner_goal
- expected_artifact
- allowed_contours
- blocked_actions
- pass_criteria
- risk_level
- repair_policy
- owner_decision_policy
- bundle_expectations

Validation:
- reject missing identity fields
- reject unknown contour labels
- reject latest/fallback language
