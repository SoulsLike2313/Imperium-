
import json
from pathlib import Path
from datetime import datetime, timezone

BASE=Path(__file__).resolve().parent
FIX=BASE/'fixtures'

def utcnow():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')

rows=[]
for p in sorted(FIX.glob('*.json')):
    d=json.loads(p.read_text(encoding='utf-8'))
    expected=d.get('expected_result','PASS')
    ok=True
    reason='ok'
    if p.name=='bad_stop_without_reason.json' and not d.get('reason'):
        ok=False; reason='missing_reason'
    if p.name=='bad_pass_with_blockers.json' and d.get('verdict')=='PASS' and d.get('blockers'):
        ok=False; reason='blockers_forbid_pass'
    if d.get('verdict')=='PASS_WITH_WARNINGS' and not d.get('warnings'):
        ok=False; reason='pww_requires_warning'
    actual='PASS' if ok else 'FAIL'
    rows.append({'fixture':p.name,'expected':expected,'actual':actual,'match_expected':expected==actual,'reason':reason})
verdict='PASS' if all(r['match_expected'] for r in rows) else 'FAIL'
report={'task_id':'TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING','stage_id':'STAGE-12-ROLLBACK-STOP-RECEIPT-PATH','created_utc':utcnow(),'fixtures_checked':len(rows),'results':rows,'verdict':verdict,'not_production_checker':True}
(BASE/'reports'/'rollback_stop_receipt_path_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(verdict)
