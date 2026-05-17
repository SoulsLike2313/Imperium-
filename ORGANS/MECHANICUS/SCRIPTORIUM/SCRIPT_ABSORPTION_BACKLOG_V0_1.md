# SCRIPT ABSORPTION BACKLOG V0.1

No script from this backlog is executed by this task unless already part of the task contract.

| Candidate | Proposed Group | Recommended Action | Source | Note |
|---|---|---|---|---|
| `ORGANS/MECHANICUS/SCRIPTORIUM/REPO_RECON/imperium_repo_recon_v0_1.py` | REPO_RECON | REGISTER_AS_IS | bootstrap task artifact | Primary read-only recon runner already proven by report outputs. |
| `scripts/verify_repo.py` | CHECKERS | REVIEW_AND_REGISTER | active entrypoint + AGENTS truth check | Core verification spine checker with current operational usage. |
| `TOOLS/run_administratum_git_cli_check.sh` | GATE_RUNNERS | REVIEW_AND_REGISTER | active entrypoint | Linux gate wrapper; requires explicit registration metadata. |
| `TOOLS/RUN_ADMINISTRATUM_GIT_CLI_CHECK.ps1` | GATE_RUNNERS | REVIEW_AND_REGISTER | active entrypoint | Windows gate wrapper; pair with shell variant for parity. |
| `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_4/tools/check_neural_base_v0_4.py` | CHECKERS | FORK_INTO_MECHANICUS | dirty snapshot commit 5082a8f | Potentially reusable checker but currently legacy test-version scoped. |
| `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_4/tools/build_neural_base_snapshot_v0_4.py` | BUILDERS | FORK_INTO_MECHANICUS | dirty snapshot commit 5082a8f | Snapshot builder candidate with test-version assumptions. |
| `ARTIFACTS/TASK-20260508-0014-SCRIPT-REPAIR-TASK-STAGE-RUN-BARRIER-LEDGER-PROVENANCE-V1/02_OUTPUTS/TOOL_SNAPSHOT/imperium_pipeline/barrier_verify.py` | CHECKERS | REVIEW_AND_REGISTER | repo recon unregistered sample | Pipeline integrity checker candidate found in artifact snapshot. |
| `ARTIFACTS/TASK-20260508-0014-SCRIPT-REPAIR-TASK-STAGE-RUN-BARRIER-LEDGER-PROVENANCE-V1/02_OUTPUTS/TOOL_SNAPSHOT/imperium_pipeline/final_bundle_assemble.py` | EXPORTERS | REVIEW_AND_REGISTER | repo recon unregistered sample | Bundle assembler candidate; requires boundary and portability checks. |
| `.kilo/kilo.json` | VISUAL_TOOLS | KEEP_AS_NEGATIVE_REFERENCE | dirty snapshot commit 5082a8f | Not a canonical runtime tool; preserve as negative sample. |
| `KILO_TEST/neural_map_optimized.html` | VISUAL_TOOLS | KEEP_AS_NEGATIVE_REFERENCE | dirty snapshot commit 5082a8f | Visual sandbox sample; no runtime adoption without dedicated gate. |

## Group Summary
- BUILDERS: 1
- CHECKERS: 3
- EXPORTERS: 1
- GATE_RUNNERS: 2
- REPO_RECON: 1
- VISUAL_TOOLS: 2

## Next Registration Task
- TASK-20260517-UNQUISITION-EXTEREMINATUS-SCRIPTORIUM-REGISTRATION-GATE-V0_1
