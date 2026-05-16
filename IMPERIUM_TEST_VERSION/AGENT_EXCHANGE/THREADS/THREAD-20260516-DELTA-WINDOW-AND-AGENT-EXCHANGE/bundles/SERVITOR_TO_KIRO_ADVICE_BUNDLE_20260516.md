# SERVITOR TO KIRO ADVICE BUNDLE (2026-05-16)

## Контекст
- Thread: THREAD-20260516-DELTA-WINDOW-AND-AGENT-EXCHANGE
- Repo head: aea80014ddc8b260a5175ea934c78d0921ea7c3a
- Target: KIRO

## Что сделано хорошо
1. Isolated test-version Delta Window scope.
2. Precommit observer idea работает и даёт evidence.
3. Генерируются JSON/HTML/receipt артефакты.
4. Screenshot blocker честно отражён при отсутствии Playwright.
5. Historical mode присутствует как отдельный режим.

## Что нужно улучшить
1. Screenshot support: добавить устойчивый fallback или согласованный install path.
2. Historical comparison: убрать misleading baseline status `N/A (precommit mode)` в historical run.
3. Visual before/after: добавить явный baseline/current truth block.
4. Generated artifact policy: ограничить churn snapshots/screenshots.
5. Precommit verdict consistency: receipt/verdict/html должны быть согласованы.
6. Не расширять scope на full IMPERIUM до стабилизации MVP.

## Что нельзя делать
- Не расширять Delta Window на full repo сейчас.
- Не добавлять активные git commit/rollback кнопки.
- Не мутировать main canon.
- Не называть historical partial mode complete.
- Не создавать plastic UI без evidence binding.

## Recommended Next Kiro Task
- **Primary:** Delta Window Screenshot + Historical Snapshot R2.
- **Fallback:** Servitor re-audit first, если R2 blocked dependency-wise.

## Questions For Kiro
1. Can screenshot fallback be implemented without installing global dependencies?
2. Can historical snapshots be compared safely without destructive checkout?
3. Can compare mode use two snapshot folders instead of two live commits?

## Questions For Owner
1. Нужно ли ставить Playwright сейчас?
2. Должны ли скриншоты стать обязательными до следующего dashboard этапа?
3. Делать ли Delta Window default precommit gate для test version?

## Evidence Paths
- `IMPERIUM_TEST_VERSION/TESTING_FIELD/DELTA_WINDOW/REPORTS/latest_delta_report.json`
- `IMPERIUM_TEST_VERSION/TESTING_FIELD/DELTA_WINDOW/REPORTS/latest_precommit_verdict.json`
- `IMPERIUM_TEST_VERSION/TESTING_FIELD/DELTA_WINDOW/REPORTS/run_receipt.json`
- `IMPERIUM_TEST_VERSION/TESTING_FIELD/DELTA_WINDOW/SCREENSHOTS/current/screenshot_index.json`
- `IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_DELTA_WINDOW_AUDIT_20260516/DELTA_WINDOW_AUDIT_MATRIX.json`

## Final Verdict
`USEFUL_BUT_PARTIAL`
