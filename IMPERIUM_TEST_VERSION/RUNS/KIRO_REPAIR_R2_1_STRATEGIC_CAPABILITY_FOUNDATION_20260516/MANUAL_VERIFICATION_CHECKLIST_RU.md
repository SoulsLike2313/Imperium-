# MANUAL VERIFICATION CHECKLIST

- [ ] Открыть Agent Exchange Window (`AGENT_EXCHANGE\agent_exchange_window.html`)
- [ ] Открыть Strategic Capability Window (`STRATEGIC_CAPABILITIES\strategic_capability_window.html`)
- [ ] Открыть Delta Window (`TESTING_FIELD\DELTA_WINDOW\delta_window.html`)
- [ ] Проверить Owner guide (`RUNS\KIRO_DELTA_R2_AGENT_EXCHANGE_WINDOW_R1_20260516\OWNER_USAGE_GUIDE_RU.md`)
- [ ] Проверить финальный отчёт (`RUNS\KIRO_REPAIR_R2_1_STRATEGIC_CAPABILITY_FOUNDATION_20260516\OWNER_FINAL_REPORT_RU.md`)
- [ ] Запустить стратегический checker: `python .\TOOLS\check_strategic_capability_foundation.py`
- [ ] Запустить CLI health: `python .\STRATEGIC_CAPABILITIES\CLI_AGENT_PORT\imperium_cli_agent_port.py --mode health`
- [ ] Запустить CLI inspect-capabilities: `python .\STRATEGIC_CAPABILITIES\CLI_AGENT_PORT\imperium_cli_agent_port.py --mode inspect-capabilities`
- [ ] Запустить CLI summarize sample: `python .\STRATEGIC_CAPABILITIES\CLI_AGENT_PORT\imperium_cli_agent_port.py --mode summarize --input .\STRATEGIC_CAPABILITIES\CLI_AGENT_PORT\sample_request.json`
- [ ] Запустить local LLM health check: `python .\STRATEGIC_CAPABILITIES\LOCAL_LLM_PORT\local_llm_health_check.py`
- [ ] Проверить distributed contour manual confirmation status (`RUNS\KIRO_REPAIR_R2_1_STRATEGIC_CAPABILITY_FOUNDATION_20260516\DISTRIBUTED_CONTOUR_DRYRUN_RECEIPT.json`)
- [ ] Убедиться, что нет fake green (особенно distinction scope vs quality)
- [ ] Убедиться, что main canon вне `IMPERIUM_TEST_VERSION` не затронут
