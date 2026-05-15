
import json
from pathlib import Path
from datetime import datetime, timezone

BASE=Path(__file__).resolve().parent
FIX=BASE/'fixtures'

def utcnow():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')

def evaluate(d):
    for f in ['generated_at_utc','git_head','checked_at_utc','expires_after_seconds','stale_status']:
        if f not in d:
            return False, f'missing_{f}'
    status=str(d.get('status','')).upper()
    stale=str(d.get('stale_status','unknown')).lower()
    if stale not in {'fresh','stale','unknown','not_applicable'}:
        return False,'invalid_stale_status'
    if stale in {'stale','unknown'} and status=='GREEN':
        return False,'stale_or_unknown_green'
    if stale in {'stale','unknown'} and status=='PASS':
        return False,'stale_or_unknown_pass'
    return True,'ok'

rows=[]
for p in sorted(FIX.glob('*.json')):
    d=json.loads(p.read_text(encoding='utf-8'))
    ok, reason=evaluate(d)
    expected=d.get('expected_result','FAIL')
    expected_ok=expected=='PASS'
    rows.append({'fixture':p.name,'expected':expected,'actual':'PASS' if ok else 'FAIL','match_expected':ok==expected_ok,'reason':reason})

verdict='PASS' if all(r['match_expected'] for r in rows) else 'FAIL'
report={
 'task_id':'TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING',
 'stage_id':'STAGE-08-STALE-STATUS-CHECKERS',
 'created_utc':utcnow(),
 'checker_path':'CHECKS/STALE_STATUS/stale_status_stage_local_check.py',
 'fixtures_checked':len(rows),
 'fresh_expected_pass':2,
 'stale_expected_fail':2,
 'unknown_expected_fail':1,
 'missing_field_expected_fail':2,
 'actual_results':rows,
 'warnings':[],
 'blockers':[] if verdict=='PASS' else ['stale_checker_expectation_mismatch'],
 'verdict':verdict,
 'coverage_limitations':['stage_local_fixtures_only','not_production_checker'],
 'not_production_checker':True
}
(BASE/'stale_status_check_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(verdict)
