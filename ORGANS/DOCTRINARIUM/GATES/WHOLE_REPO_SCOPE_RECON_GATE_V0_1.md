# Whole-Repo Scope Recon Gate V0.1

- gate_id: `GATE-U14-WHOLE-REPO-SCOPE-RECON`
- status: `DRAFT_ACTIVE_FOR_PLANNING`

## Purpose
- Large whole-system tasks must perform relevant repo-wide recon before editing.

## Applies To
- `whole_repo_tasks`
- `multi_organ_fusion_tasks`
- `high_scope_contract_tasks`

## Required Inputs
- `task_scope`
- `recon_targets`
- `forbidden_paths`

## Required Evidence
- `repo_recon_summary`
- `scope_map`
- `touched_path_plan`

## Pass Condition
- Task demonstrates relevant whole-repo reconnaissance tied to requested scope.

## Fail Condition
- Task edits doctrine/roadmap scope without relevant whole-repo recon evidence.

## Stop Condition
- Scope is large but recon evidence is missing or obviously partial.
