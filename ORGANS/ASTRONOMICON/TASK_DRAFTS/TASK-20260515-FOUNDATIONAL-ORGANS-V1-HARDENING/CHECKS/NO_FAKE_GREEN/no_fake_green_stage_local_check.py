
import json
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent
FIX = BASE / 'fixtures'

def utcnow():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')

def eval_fixture(d):
    status = str(d.get('status','')).upper()
    evidence = d.get('evidence_paths') or []
    warnings = d.get('warnings') or []
    blockers = d.get('blockers') or []
    freshness = d.get('freshness','unknown')
    if status in {'PASS','GREEN','READY','COMPLETE'} and len(evidence)==0:
        return False, 'pass_without_evidence'
    if status == 'PASS_WITH_WARNINGS' and len(warnings)==0:
        return False, 'pww_without_warning_list'
    if status == 'PASS' and len(warnings)>0:
        return False, 'pass_has_warnings'
    if len(blockers)>0 and status in {'PASS','GREEN'}:
        return False, 'blockers_forbid_pass'
    if status == 'GREEN' and not d.get('source_report_path'):
        return False, 'green_missing_source_report'
    if d.get('action_enabled') and (not d.get('expected_receipt_path') or not d.get('failure_behavior')):
        return False, 'enabled_action_without_receipt_contract'
    if d.get('script_visible') and (not d.get('script_exists')) and not d.get('disabled_reason'):
        return False, 'visible_script_without_last_report_or_disabled_reason'
    if freshness in {'stale','unknown'} and status == 'GREEN':
        return False, 'stale_or_unknown_green'
    if d.get('claims_production_pass') and d.get('fixture_only'):
        return False, 'fixture_claims_production_pass'
    return True, 'ok'

results=[]
actual_pass=0
actual_fail=0
for p in sorted(FIX.glob('*.json')):
    d=json.loads(p.read_text(encoding='utf-8'))
    ok, reason = eval_fixture(d)
    expected = d.get('expected_result','FAIL')
    expected_ok = expected == 'PASS'
    match = (ok == expected_ok)
    if ok:
        actual_pass += 1
    else:
        actual_fail += 1
    results.append({'fixture':p.name,'expected':expected,'actual':'PASS' if ok else 'FAIL','match_expected':match,'reason':reason})

bad = [r for r in results if r['fixture'].startswith('bad_') and r['actual']=='FAIL' and r['match_expected']]
good = [r for r in results if r['fixture'].startswith('good_') and r['actual']=='PASS' and r['match_expected']]
verdict = 'PASS' if all(r['match_expected'] for r in results) else 'FAIL'
report={
  'task_id':'TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING',
  'stage_id':'STAGE-07-NO-FAKE-GREEN-CHECKERS',
  'created_utc': utcnow(),
  'checker_path':'CHECKS/NO_FAKE_GREEN/no_fake_green_stage_local_check.py',
  'fixtures_checked': len(results),
  'expected_pass_count': 1,
  'expected_fail_count': len(results)-1,
  'actual_pass_count': actual_pass,
  'actual_fail_count': actual_fail,
  'bad_fixtures_detected': [r['fixture'] for r in bad],
  'good_fixtures_passed': [r['fixture'] for r in good],
  'warnings': [],
  'blockers': [] if verdict=='PASS' else ['fixture_expectation_mismatch'],
  'verdict': verdict,
  'coverage_limitations':['stage_local_fixtures_only','not_production_checker'],
  'not_production_checker': True,
  'results': results,
}
(BASE/'no_fake_green_check_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(verdict)
