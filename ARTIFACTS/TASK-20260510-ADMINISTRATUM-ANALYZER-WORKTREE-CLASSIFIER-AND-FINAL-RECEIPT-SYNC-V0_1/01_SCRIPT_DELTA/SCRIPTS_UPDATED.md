Updated scripts:
- TOOLS/administratum_analyze_git_local_context.ps1
- TOOLS/build_chat_compilation_from_analysis.ps1
- ORGANS/ADMINISTRATUM/UTILITY/run_administratum_context_bundle_workflow.ps1

Main changes:
- Added worktree classifier and category/action mapping.
- Fixed owner action logic for matched HEADs + dirty worktree.
- Added supplemental receipt sync support.
- Added bundle warnings based on classifier and boundary verdict.
