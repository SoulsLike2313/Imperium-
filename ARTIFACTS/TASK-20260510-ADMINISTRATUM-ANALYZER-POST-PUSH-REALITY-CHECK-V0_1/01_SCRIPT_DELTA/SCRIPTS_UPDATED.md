# SCRIPTS UPDATED

- TOOLS/administratum_analyze_git_local_context.ps1
- TOOLS/build_chat_compilation_from_analysis.ps1
- ORGANS/ADMINISTRATUM/UTILITY/run_administratum_context_bundle_workflow.ps1

Key changes:
- Added -PostPushRealityCheck and v0.2 analysis schema.
- Added git reality matching checks and owner_action decision block.
- Builder now consumes analyzer v0.2 and records warnings when git/boundary verdicts are not clean.
- Workflow supports AnalyzeOnly and BuildBundle switches.
