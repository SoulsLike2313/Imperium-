#!/usr/bin/env python3
"""
CANDIDATE MODEL
Implements LAST_STRONG_COMMIT vs COMMIT_CANDIDATE comparison model.

Usage:
    py -3 candidate_model.py --baseline HEAD --candidate worktree
    py -3 candidate_model.py --baseline <commit_sha> --candidate <commit_sha>
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_commit_info(repo_root, ref):
    """Get commit information."""
    if ref == 'worktree':
        return {
            'type': 'worktree',
            'ref': 'worktree',
            'sha': None,
            'label': 'Current worktree (uncommitted)',
            'message': None,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    try:
        sha = subprocess.run(
            ['git', 'rev-parse', ref],
            cwd=repo_root, capture_output=True, text=True
        ).stdout.strip()
        
        log = subprocess.run(
            ['git', 'log', '-1', '--format=%s', ref],
            cwd=repo_root, capture_output=True, text=True
        ).stdout.strip()
        
        timestamp = subprocess.run(
            ['git', 'log', '-1', '--format=%cI', ref],
            cwd=repo_root, capture_output=True, text=True
        ).stdout.strip()
        
        return {
            'type': 'commit',
            'ref': ref,
            'sha': sha,
            'label': f'{sha[:8]} - {log[:50]}',
            'message': log,
            'timestamp': timestamp
        }
    except Exception as e:
        return {
            'type': 'error',
            'ref': ref,
            'error': str(e)
        }


def get_worktree_status(repo_root, scope_path):
    """Get worktree status for scope."""
    rel_scope = scope_path.relative_to(repo_root)
    
    # Staged changes
    staged = subprocess.run(
        ['git', 'diff', '--cached', '--name-status', '--', str(rel_scope)],
        cwd=repo_root, capture_output=True, text=True
    ).stdout.strip()
    
    # Unstaged changes
    unstaged = subprocess.run(
        ['git', 'diff', '--name-status', '--', str(rel_scope)],
        cwd=repo_root, capture_output=True, text=True
    ).stdout.strip()
    
    # Untracked files
    untracked = subprocess.run(
        ['git', 'ls-files', '--others', '--exclude-standard', '--', str(rel_scope)],
        cwd=repo_root, capture_output=True, text=True
    ).stdout.strip()
    
    # Check main canon
    main_staged = subprocess.run(
        ['git', 'diff', '--cached', '--name-only'],
        cwd=repo_root, capture_output=True, text=True
    ).stdout.strip()
    
    main_unstaged = subprocess.run(
        ['git', 'diff', '--name-only'],
        cwd=repo_root, capture_output=True, text=True
    ).stdout.strip()
    
    main_untracked = subprocess.run(
        ['git', 'ls-files', '--others', '--exclude-standard'],
        cwd=repo_root, capture_output=True, text=True
    ).stdout.strip()
    
    # Check if main canon touched
    main_canon_files = []
    for line in (main_staged + '\n' + main_unstaged + '\n' + main_untracked).split('\n'):
        if line and not line.startswith(str(rel_scope)):
            main_canon_files.append(line)
    
    is_clean = not (staged or unstaged or untracked)
    
    return {
        'is_clean': is_clean,
        'staged_count': len(staged.split('\n')) if staged else 0,
        'unstaged_count': len(unstaged.split('\n')) if unstaged else 0,
        'untracked_count': len(untracked.split('\n')) if untracked else 0,
        'main_canon_touched': len(main_canon_files) > 0,
        'main_canon_files': main_canon_files[:10],
        'status_label': 'CLEAN' if is_clean else 'DIRTY'
    }


def build_candidate_model(repo_root, scope_path, baseline_ref='HEAD', candidate_ref='worktree'):
    """Build candidate comparison model."""
    repo_root = Path(repo_root).resolve()
    scope_path = Path(scope_path).resolve()
    
    baseline = get_commit_info(repo_root, baseline_ref)
    candidate = get_commit_info(repo_root, candidate_ref)
    worktree = get_worktree_status(repo_root, scope_path)
    
    # Determine if commit is safe
    can_commit = True
    blockers = []
    
    if worktree['main_canon_touched']:
        can_commit = False
        blockers.append('Main canon files modified outside test version')
    
    if worktree['is_clean'] and candidate_ref == 'worktree':
        blockers.append('No changes to commit')
    
    return {
        'model_id': f'CANDIDATE-{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'repo_root': str(repo_root),
        'scope_root': str(scope_path),
        'baseline': {
            'label': 'LAST_STRONG_COMMIT',
            'info': baseline
        },
        'candidate': {
            'label': 'COMMIT_CANDIDATE',
            'info': candidate
        },
        'worktree': worktree,
        'comparison': {
            'baseline_ref': baseline_ref,
            'candidate_ref': candidate_ref,
            'scope': 'IMPERIUM_TEST_VERSION_ONLY',
            'main_canon_touched': worktree['main_canon_touched'],
            'can_commit': can_commit,
            'blockers': blockers
        }
    }


def main():
    parser = argparse.ArgumentParser(description='Build candidate comparison model')
    parser.add_argument('--baseline', default='HEAD', help='Baseline commit ref')
    parser.add_argument('--candidate', default='worktree', help='Candidate ref (commit or worktree)')
    parser.add_argument('--repo-root', help='Repository root')
    parser.add_argument('--scope', help='Scope path (test version root)')
    parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    # Determine paths
    script_dir = Path(__file__).parent
    
    if args.scope:
        scope_path = Path(args.scope).resolve()
    else:
        scope_path = script_dir.parent.parent  # DELTA_WINDOW -> TESTING_FIELD -> IMPERIUM_TEST_VERSION
    
    if args.repo_root:
        repo_root = Path(args.repo_root).resolve()
    else:
        repo_root = scope_path.parent  # IMPERIUM_TEST_VERSION -> IMPERIUM
    
    model = build_candidate_model(repo_root, scope_path, args.baseline, args.candidate)
    
    # Output
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = script_dir / 'REPORTS' / 'latest_candidate_delta.json'
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(model, f, indent=2, ensure_ascii=False)
    
    print(f'Candidate model saved: {output_path}')
    print(f'Baseline: {model["baseline"]["info"].get("label", "unknown")}')
    print(f'Candidate: {model["candidate"]["info"].get("label", "unknown")}')
    print(f'Worktree: {model["worktree"]["status_label"]}')
    print(f'Main canon touched: {model["comparison"]["main_canon_touched"]}')
    print(f'Can commit: {model["comparison"]["can_commit"]}')
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
