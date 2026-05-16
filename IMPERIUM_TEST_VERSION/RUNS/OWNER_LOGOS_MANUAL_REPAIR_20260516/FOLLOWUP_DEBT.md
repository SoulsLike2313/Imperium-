# Followup Debt

## Immediate technical debt

| Debt | Priority | Notes |
|---|---:|---|
| Fix 5 HIGH hardcoded PASS findings | HIGH | Anti-Pattern Scanner debt |
| Fix unconditional sys.exit(0) | HIGH | Administratum self_inventory |
| Decide LOW bare-except policy | MEDIUM | Some may be acceptable if logged |
| Register patch utilities or archive them | MEDIUM | Current TOOLS patch files are evidence but may need classification |
| Add narrative repair report to Second Brain | HIGH | This package is the first seed |
| Create Second Brain zone map | HIGH | Needed for future agent navigation |

## Strategic debt

The system needs a real Second Brain architecture with:
- Owner Memory;
- Past Memory;
- Future Memory;
- Owner Comments Mesh;
- Agent/CLI/API Ports;
- Local LLM Ports;
- Distributed Contours;
- Product/Distribution Memory;
- Task Intake and Execution Memory;
- Evidence and Receipts Memory;
- Rules / Forbidden Actions / PASS-FAIL criteria.

## Next recommended task

Build Second Brain V0.2 / Memory Zone Map inside IMPERIUM_TEST_VERSION only.

Do not promote to main canon yet.
Do not claim production readiness.
Build a working mock/form first.
