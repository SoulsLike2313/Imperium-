# REPAIR_TEST_RESULTS

Task:
TASK-20260508-0014C-TOOL-ROOT-RUNTIME-CLOSURE-ADDRESS-REGISTRY-READONLY-EXPLORER-AND-DRYRUN-PROOF-V1

1) Python compile
Result: PASS
Evidence: 07_REPORTS/PYTHON_FILES_COMPILE_LIST.txt and successful py_compile run for all scripts under 06_TOOLS.

2) final_bundle_assemble --help runtime smoke
Result: PASS
Evidence: INSTALLED_ROOT_RUNTIME_SMOKE_RECEIPT.json and 07_REPORTS/final_bundle_assemble_help_stdout.txt.

3) Dependency closure check
Result: PASS
Evidence: DEPENDENCY_CLOSURE_REPORT.md.

4) Local final assembly dry-run
Result: PASS
Evidence: LOCAL_FINAL_ASSEMBLY_DRYRUN_RECEIPT.json and LOCAL_FINAL_ASSEMBLY_DRYRUN_REPORT.md.

5) Internal SHA verification after extraction
Result: PASS
Evidence: LOCAL_FINAL_ASSEMBLY_DRYRUN_RECEIPT.json -> checks.internal_sha_ok=true.

6) FINAL_PROVENANCE no-PENDING
Result: PASS
Evidence: LOCAL_FINAL_ASSEMBLY_DRYRUN_RECEIPT.json -> checks.final_provenance_no_pending=true.

7) Zip path hygiene
Result: PASS
Evidence: LOCAL_FINAL_ASSEMBLY_DRYRUN_RECEIPT.json -> checks.zip_posix_hygiene_ok=true.

8) External .sha256 portability
Result: PASS
Evidence: LOCAL_FINAL_ASSEMBLY_DRYRUN_RECEIPT.json -> checks.external_sha_filename_only=true.

9) Read-only explorer summary mode
Result: PASS
Evidence: 07_REPORTS/readonly_explorer_summary.txt, exit code 0.

10) Read-only explorer map mode
Result: PASS
Evidence: 07_REPORTS/readonly_explorer_map.txt, exit code 0.

11) Registry JSON parse check
Result: PASS
Evidence: 07_REPORTS/REGISTRY_PARSE_AND_ACTIVE_CHECK.json -> index_parse_ok=true.

12) Active tools present in registry
Result: PASS
Evidence: 07_REPORTS/REGISTRY_PARSE_AND_ACTIVE_CHECK.json -> active_tool_count > 0.

Scope confirmation:
- No VM2 contact.
- No real PC↔VM2 E2E execution.
- No THRONE transfer.
- No watcher/background automation.
