
import json
from pathlib import Path
from datetime import datetime, timezone

BASE=Path(__file__).resolve().parent
FIX=BASE/'fixtures'
MOJI=['Р’','Р°','Рµ','Ð','Ñ','вЂ','�']
FORBIDDEN=['E:/IMPERIUM_CONTEXT','E:/IMPERIUM_LOCAL','E:/IMPERIUM_PRIVATE','OUTBOX/','INBOX/','.imperium_runtime/','tmp/']

def utcnow():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')

rows=[]
# json fixtures
for p in sorted(FIX.glob('*.json')):
    d=json.loads(p.read_text(encoding='utf-8'))
    expected=d.get('expected_result','PASS')
    actual='PASS'
    reason='ok'
    status_key=d.get('status_key')
    if status_key and any(ord(ch)>127 for ch in status_key):
        actual='FAIL'; reason='non_english_canonical_status_key'
    path=d.get('path','')
    if any(path.startswith(x) or x in path for x in FORBIDDEN):
        actual='FAIL'; reason='forbidden_repo_path'
    rows.append({'fixture':p.name,'expected':expected,'actual':actual,'match_expected':expected==actual,'reason':reason})

# text fixture
txt=(FIX/'bad_mojibake_text_sample.txt').read_text(encoding='utf-8')
has_moji=any(m in txt for m in MOJI)
rows.append({'fixture':'bad_mojibake_text_sample.txt','expected':'FAIL','actual':'FAIL' if has_moji else 'PASS','match_expected':has_moji,'reason':'mojibake_marker_detected' if has_moji else 'not_detected'})

verdict='PASS' if all(r['match_expected'] for r in rows) else 'FAIL'
report={
 'task_id':'TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING','stage_id':'STAGE-17-UTF8-REPO-PURITY-HARDENING-CHECKS','created_utc':utcnow(),
 'checker_path':'CHECKS/UTF8_REPO_PURITY/utf8_repo_purity_stage_local_check.py','fixtures_checked':len(rows),'good_fixtures_passed':[r['fixture'] for r in rows if r['expected']=='PASS' and r['actual']=='PASS'],'bad_fixtures_detected':[r['fixture'] for r in rows if r['expected']=='FAIL' and r['actual']=='FAIL'],
 'warnings':[],'blockers':[] if verdict=='PASS' else ['utf8_repo_purity_fixture_mismatch'],'coverage_limitations':['stage_local_fixtures_only','not_production_checker'],'not_production_checker':True,'verdict':verdict,'results':rows
}
(BASE/'utf8_repo_purity_check_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(verdict)
