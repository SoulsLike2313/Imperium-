# BASE MANDATORY GATES V0.1

| Gate | What It Prevents | When It Applies | Required Evidence | STOP Trigger |
|---|---|---|---|---|
| GATE-U00-GIT-TRUTH | Running on wrong git truth baseline. | All operational tasks. | HEAD/branch/status receipt + expected hash match. | HEAD mismatch or unresolved truth conflict. |
| GATE-U01-ROLE-ACK | Unaudited execution without admission contract. | All tasks before edits. | Complete GATE_ACK block. | Missing GATE_ACK or rejected stop conditions. |
| GATE-U02-SCOPE-BOUNDARY | Out-of-scope or forbidden path edits. | All tasks with filesystem changes. | Allowed/forbidden paths + diff path proof. | Forbidden path in diff or unknown scope. |
| GATE-U03-NO-FEATURE-DRIFT | Accidental behavior drift in bounded tasks. | Hardening/audit/visual-boundary tasks. | Before-after behavior notes + diff scope. | Unplanned runtime/feature mutation. |
| GATE-U04-EVIDENCE-RECEIPT | Unsupported PASS/quality claims. | All tasks with verdicts. | Required reports/receipts exist and parse. | Missing critical receipt evidence. |
| GATE-U05-STOP-CONDITIONS | Silent continuation under uncertainty. | All tasks. | Accepted stop-condition list in GATE_ACK. | Stop conditions absent or bypassed. |
| GATE-U06-OWNER-GATE | Risky/destructive acts without Owner approval. | High-risk/destructive tasks. | Owner gate reference/receipt. | Risky action without Owner gate. |
| GATE-U07-ROLLBACK-PATH | Non-recoverable mutable operations. | Mutable/refactor tasks. | Rollback plan receipt. | Rollback impossible with elevated risk. |
| GATE-U08-REPO-PURITY | Hidden repo pollution/drift. | All tasks. | Before/after git status + diff summary. | Unexpected unrelated changes discovered. |
| GATE-U09-NO-FAKE-GREEN | PASS without evidence. | All tasks. | Checker/test/receipt proofs. | PASS claim without hard evidence. |
| GATE-U10-PATH-TRUTH | False touched-path reporting. | All tasks with edits. | Path declaration vs actual diff comparison. | Declaration mismatches actual changes. |
| GATE-U11-BEFORE-AFTER | Unverifiable improvement claims. | All non-trivial tasks. | Before and after state receipts. | No comparable baseline evidence. |
| GATE-U12-REPORT-OUTPUT-BUDGET | Report avalanche and evidence dump pollution. | All scanner/checker/report-producing tasks. | Report budget config + compact report metrics + omitted/raw_dump status. | Output exceeds budget or unlimited raw dump without Owner gate. |
| GATE-U13-PYTHON-TYPE-SAFETY | Promotion of type-chaotic Python scripts into reusable/core operational roles. | Python script promotion tasks. | Script maturity classification + type-safety policy/backlog + strict evidence where required. | Promotion attempted without required strict evidence or with unresolved type-chaos at contract boundaries. |
| GATE-UI00-TRUTH-BINDING | Visual/UI claims detached from backend truth. | UI/visual/boundary tasks. | Truth-binding report linking claims to data receipts. | UI readiness claimed while backend broken. |
| GATE-VIS00-PERFORMANCE-BUDGET | Unmeasured performance claims. | Performance/visual tasks. | Performance measurement receipt. | Performance claim without metrics. |
| GATE-VIS01-DECORATIVE-SEMANTIC-SPLIT | Decorative tasks altering semantic corridor. | Visual/decorative tasks. | Scope split audit evidence. | Backend/semantic change during decorative task. |
| GATE-AI00-NO-DIRECT-MODEL-COMMAND | Free-form execution without contract/gates. | All operational tasks. | Gatepack + task contract + GATE_ACK. | No contract artifacts for critical task. |
