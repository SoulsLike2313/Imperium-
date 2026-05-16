#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def main():
    script = Path(__file__).resolve()
    v05 = script.parents[1]
    audit = v05 / 'AUDIT_FRONTBACK_TRUTH_PARITY_V0_1'
    matrix = json.loads((audit / 'truth_parity_matrix_v0_1.json').read_text(encoding='utf-8'))
    binding = json.loads((audit / 'frontend_binding_inventory.json').read_text(encoding='utf-8'))
    run = json.loads((audit / 'playwright' / 'playwright_run_report.json').read_text(encoding='utf-8'))

    rows = matrix.get('rows', [])
    counts = {'TRUE':0,'PARTIAL':0,'FALSE':0,'STALE':0,'UNPROVEN':0,'STATIC_LABEL_ONLY':0,'NOT_APPLICABLE':0}
    for r in rows:
        status = r.get('parity_status','UNPROVEN')
        counts[status] = counts.get(status, 0) + 1

    hardcoded_risk = sum(1 for f in binding.get('fields',[]) if f.get('classification') in {'HARDCODED_RISK','FALLBACK_RISK','FALSE_OR_STALE_RISK'})
    total = len(rows)

    if run.get('result') != 'PASS':
        verdict = 'UNPROVEN'
    elif counts.get('FALSE',0) > 0 or counts.get('STALE',0) > 0:
        verdict = 'FAIL'
    elif counts.get('UNPROVEN',0) == 0 and counts.get('PARTIAL',0) == 0 and hardcoded_risk == 0:
        verdict = 'PASS_STRICT'
    else:
        verdict = 'PASS_WITH_LIMITATIONS'

    report = {
        'checker': 'check_frontback_truth_parity_v0_1.py',
        'timestamp_utc': utc_now(),
        'total_claims_audited': total,
        'true_count': counts.get('TRUE',0),
        'partial_count': counts.get('PARTIAL',0),
        'false_count': counts.get('FALSE',0),
        'stale_count': counts.get('STALE',0),
        'unproven_count': counts.get('UNPROVEN',0),
        'hardcoded_risk_count': hardcoded_risk,
        'verdict': verdict,
    }
    out = audit / 'frontback_truth_parity_check_report_v0_1.json'
    out.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('frontback parity checker report:', out)
    print('verdict:', verdict)
    return 0 if verdict in {'PASS_STRICT','PASS_WITH_LIMITATIONS'} else 1

if __name__ == '__main__':
    raise SystemExit(main())
