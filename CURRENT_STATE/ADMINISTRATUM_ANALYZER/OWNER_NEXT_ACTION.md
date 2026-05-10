# OWNER NEXT ACTION

- recommended_owner_action: RUN_CHAT_COMPILATION_SAFE
- reason: Public memory is ready but target requires local/private context.
- command_to_run_if_bundle_needed: powershell -ExecutionPolicy Bypass -File E:\\IMPERIUM\\ORGANS\\ADMINISTRATUM\\UTILITY\\run_administratum_context_bundle_workflow.ps1 -Target FULL_IMPERIUM_SUMMARY -BuildBundle
- expected_zip_location: E:\\IMPERIUM\\CHAT_COMPILATIONS_LOCAL\\FULL_IMPERIUM_CONTEXT_<timestamp>.zip

Warning: if MANUAL_REVIEW_REQUIRED, review worktree classifier before any bundle build.
