#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def is_non_canon_placeholder(path: Path) -> bool:
    if not path.exists():
        return False
    txt = path.read_text(encoding='utf-8-sig', errors='replace')
    markers = [
        'THIS IS A NON-CANON PLACEHOLDER.',
        'OWNER REVIEW REQUIRED.',
        'DO NOT USE AS CANON DOCTRINE.',
        'status: DRAFT_PLACEHOLDER_OWNER_REVIEW_REQUIRED',
        'not_canon: true'
    ]
    return all(m in txt for m in markers[:3]) or any(m in txt for m in markers[3:])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--recipe-path', required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--root', default=r'E:\IMPERIUM')
    args = parser.parse_args()

    root = Path(args.root)
    task_id = args.task_id
    recipe_path = Path(args.recipe_path)
    doctr = root / 'ORGANS' / 'DOCTRINARIUM'
    laws_dir = doctr / 'LAWS'
    doctrine_dir = doctr / 'DOCTRINE'
    artifact = root / 'ARTIFACTS' / task_id

    mandatory_file = laws_dir / 'MANDATORY_LAWS.json'
    law_names = []
    blockers = []
    if mandatory_file.exists():
        mandatory = json.loads(mandatory_file.read_text(encoding='utf-8-sig'))
        law_names = mandatory.get('required_files', [])
    else:
        blockers.append(f'Missing mandatory laws list: {mandatory_file}')

    missing_laws = [name for name in law_names if not (laws_dir / name).exists()]
    if missing_laws:
        blockers.append('Missing mandatory law files: ' + ', '.join(missing_laws))

    passport = doctrine_dir / 'PASSPORT_OF_EMPEROR.md'
    constitution = doctrine_dir / 'CONSTITUTION_OF_IMPERIUM.md'
    has_passport = passport.exists()
    has_constitution = constitution.exists()
    passport_placeholder = is_non_canon_placeholder(passport)
    constitution_placeholder = is_non_canon_placeholder(constitution)
    canon_ready = has_passport and has_constitution and not passport_placeholder and not constitution_placeholder

    hashes = {}
    hashed_sources = [recipe_path, mandatory_file]
    for name in law_names:
        hashed_sources.append(laws_dir / name)
    bootstrap_doc = doctrine_dir / 'DOCTRINE_BOOTSTRAP_MINIMUM_LAWS.md'
    if bootstrap_doc.exists():
        hashed_sources.append(bootstrap_doc)
    if has_passport:
        hashed_sources.append(passport)
    if has_constitution:
        hashed_sources.append(constitution)

    for src in hashed_sources:
        if src.exists():
            hashes[str(src)] = sha256_of_file(src)

    mode = 'SMOKE_TEST'
    try:
        recipe = json.loads(recipe_path.read_text(encoding='utf-8-sig'))
        mode = recipe.get('mode', 'SMOKE_TEST')
    except Exception as ex:
        blockers.append(f'Recipe read failed: {ex}')

    if blockers:
        verdict = 'FAIL'
        next_action = 'Fix doctrinarium required files before rerun.'
    elif canon_ready:
        verdict = 'CANON_DOCTRINE_READY'
        next_action = 'Proceed to Officio Agentis.'
    else:
        if mode == 'SMOKE_TEST':
            verdict = 'BOOTSTRAP_NOT_CANON'
            next_action = 'Proceed in bootstrap smoke mode; canon docs still required for real tasks.'
        else:
            verdict = 'BLOCKED_MISSING_DOCTRINE_FOR_REAL_TASK'
            blockers.append('Passport/Constitution missing or placeholder for non-smoke mode.')
            next_action = 'Provide canonical doctrine documents or switch to smoke mode.'

    receipt = {
        'schema_version': 'RECEIPT_V0_1',
        'task_id': task_id,
        'run_id': args.run_id,
        'stage_id': None,
        'actor': 'PC_SERVITOR',
        'organ': 'DOCTRINARIUM',
        'input_paths': [str(recipe_path), str(mandatory_file)],
        'output_paths': [
            str(artifact / '03_RECEIPTS' / '00_doctrinarium_preflight_receipt.json'),
            str(doctr / 'RECEIPTS' / task_id / '00_doctrinarium_preflight_receipt.json')
        ],
        'hashes': hashes,
        'verdict': verdict,
        'blockers': blockers,
        'next_action': next_action,
        'doctrine_status': {
            'passport_exists': has_passport,
            'constitution_exists': has_constitution,
            'passport_placeholder': passport_placeholder,
            'constitution_placeholder': constitution_placeholder,
            'canon_ready': canon_ready
        },
        'created_at': now_iso(),
        'no_delete_policy_observed': True,
        'no_archive_scan_policy_observed': True,
        'no_throne_policy_observed': True,
        'notes_ru': 'Прогон доктринариума завершен. При отсутствии канонических документов включен bootstrap-режим только для smoke-теста.'
    }

    r1 = artifact / '03_RECEIPTS' / '00_doctrinarium_preflight_receipt.json'
    r2 = doctr / 'RECEIPTS' / task_id / '00_doctrinarium_preflight_receipt.json'
    write_json(r1, receipt)
    write_json(r2, receipt)

    if verdict in {'FAIL', 'BLOCKED_MISSING_DOCTRINE_FOR_REAL_TASK'}:
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
