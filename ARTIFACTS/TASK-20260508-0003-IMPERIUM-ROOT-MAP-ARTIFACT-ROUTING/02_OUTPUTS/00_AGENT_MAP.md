# ARTIFACTS — AGENT MAP

Назначение:
Здесь хранятся доказательства выполненных задач IMPERIUM.

Главное:
Каждая задача получает отдельную папку:
E:\IMPERIUM\ARTIFACTS\<TASK_ID>\

Стандартная структура task artifact folder:

<TASK_ID>\
├── 00_AGENT_MAP.md
├── 01_INPUTS\
├── 02_OUTPUTS\
├── 03_RECEIPTS\
├── 04_MANIFESTS\
├── 05_HASHES\
├── 06_BUNDLES\
├── 07_REPORTS\
├── 08_OWNER_SUMMARY\
├── 09_SOURCE_POINTERS\
└── FINAL_STEP_BUNDLE\

Что сюда класть:
- task cards
- stage cards
- run cards
- receipts
- manifests
- sha256
- bundles
- barrier verdicts
- owner summaries
- route proofs
- Speculum reviews
- diagnostic evidence summaries

Что сюда нельзя класть:
- private keys
- passwords
- tokens
- .env
- cookies
- unrelated local configs
- raw secrets
- random files without TASK_ID

Статус:
Draft baseline.
