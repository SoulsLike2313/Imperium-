
import json
from pathlib import Path
from datetime import datetime, timezone

BASE=Path(__file__).resolve().parent
FIX=BASE/'fixtures'

def utcnow():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')

def validate(d):
    if not d.get('enabled'):
        if not d.get('disabled_reason'):
            return False,'disabled_without_reason'
    if d.get('enabled') and d.get('action_type') not in ('read_only_view','read_only_export'):
        if not d.get('expected_receipt_path'):
            return False,'enabled_non_read_only_without_receipt'
        if not d.get('failure_condition'):
            return False,'enabled_action_without_failure_behavior'
    if d.get('action_type')=='destructive' and d.get('enabled'):
        return False,'destructive_enabled'
    if d.get('organ_id')=='ADMINISTRATUM' and d.get('source_of_truth_owner')=='Doctrinarium':
        return False,'wrong_owner_organ'
    return True,'ok'

rows=[]
for p in sorted(FIX.glob('*.json')):
    d=json.loads(p.read_text(encoding='utf-8'))
    ok, reason=validate(d)
    expected=d.get('expected_result','PASS')
    actual='PASS' if ok else 'FAIL'
    rows.append({'fixture':p.name,'expected':expected,'actual':actual,'match_expected':expected==actual,'reason':reason})
verdict='PASS' if all(r['match_expected'] for r in rows) else 'FAIL'
report={
 'task_id':'TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING','stage_id':'STAGE-16-DASHBOARD-ACTION-RECEIPT-CONTROLS','created_utc':utcnow(),
 'checker_path':'DASHBOARD_UI/ACTION_CONTROLS/dashboard_action_receipt_control_static_check.py','fixtures_checked':len(rows),'results':rows,
 'warnings':[],'blockers':[] if verdict=='PASS' else ['action_control_fixture_mismatch'],'verdict':verdict,'not_production_checker':True
}
(BASE/'dashboard_action_receipt_control_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(verdict)
