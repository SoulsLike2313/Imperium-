# CONTINUITY_ORGAN_PORT_CONTRACT_V1

Continuity executor evolves from central scanner to orchestrator over organ self-report ports.

Current status:
- organ self-report ports are NOT_YET_AVAILABLE
- this file defines contract slots only

Future invocation pattern:
python <organ_self_report.py> --imperium-root E:\\IMPERIUM --query-file CONTINUITY_QUERY.json --output-report <ORGAN_SELF_REPORT.json> --receipt-out <ORGAN_SELF_REPORT_RECEIPT.json>

Rules:
- no fake implementation flags
- no VM2/THRONE side effects for continuity queries
- response must follow ORGAN_CONTINUITY_RESPONSE_SCHEMA_V1.json
- collector must mark missing ports as NON_FATAL_UNTIL_IMPLEMENTED
