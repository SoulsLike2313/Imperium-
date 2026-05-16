#!/usr/bin/env python3
"""
MOJIBAKE SCANNER
Detects encoding issues in repository files.

Usage:
    py -3 mojibake_scan.py --scope IMPERIUM_TEST_VERSION
    py -3 mojibake_scan.py --scope FULL_REPO --read-only
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Mojibake detection patterns
MOJIBAKE_PATTERNS = [
    # Cyrillic UTF-8 misread as CP1252
    (r'Ð[А-яЁёа-я]', 'cyrillic_utf8_as_cp1252'),
    (r'Ñ[‚€™œ\x80-\x9f]', 'cyrillic_continuation'),
    # Latin extended mojibake
    (r'Â[\s\.,;:!?\'\"]', 'latin_extended_space'),
    (r'Ã[^\w\s]', 'latin_extended_symbol'),
    # Smart quotes mojibake
    (r'â€[""''—–\x9c\x9d\x98\x99]', 'smart_quotes_mojibake'),
    # Common broken sequences
    (r'Ð\x9f', 'broken_cyrillic_p'),
    (r'Ð\x90', 'broken_cyrillic_a'),
    (r'Ð\xb0', 'broken_cyrillic_small_a'),
]

# File extensions to scan
SCAN_EXTENSIONS = {
    '.json', '.md', '.py', '.ps1', '.html', '.css', '.js',
    '.txt', '.yaml', '.yml', '.xml', '.csv'
}

# Files to skip
SKIP_PATTERNS = [
    '__pycache__',
    '.git',
    'node_modules',
    '.pyc',
    '.zip',
    '.png',
    '.jpg',
    '.gif',
    '.ico',
    '.woff',
    '.ttf',
]


def should_scan_file(path):
    """Check if file should be scanned."""
    path_str = str(path).lower()
    
    # Skip binary and cache files
    for skip in SKIP_PATTERNS:
        if skip in path_str:
            return False
    
    # Check extension
    return path.suffix.lower() in SCAN_EXTENSIONS


def detect_mojibake(content, filepath):
    """Detect mojibake patterns in content."""
    findings = []
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        for pattern, pattern_name in MOJIBAKE_PATTERNS:
            matches = re.finditer(pattern, line)
            for match in matches:
                findings.append({
                    'file': str(filepath),
                    'line': line_num,
                    'column': match.start(),
                    'pattern': pattern_name,
                    'matched_text': match.group()[:50],
                    'context': line[max(0, match.start()-20):match.end()+20][:100]
                })
    
    return findings


def classify_severity(filepath, findings):
    """Classify severity based on file type."""
    path_str = str(filepath).lower()
    
    # Blockers: schemas, protocols, state files
    if any(x in path_str for x in ['schema', 'protocol', 'state', 'index.json']):
        return 'BLOCKER'
    
    # Warnings: documentation, templates
    if any(x in path_str for x in ['.md', 'template', '.html']):
        return 'WARNING'
    
    # Info: generated files, logs
    if any(x in path_str for x in ['report', 'log', 'receipt']):
        return 'INFO'
    
    return 'WARNING'


def scan_directory(root_path, scope_label):
    """Scan directory for mojibake."""
    root = Path(root_path)
    results = {
        'scan_id': f'MOJIBAKE-{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'scope': scope_label,
        'root_path': str(root),
        'files_scanned': 0,
        'files_with_issues': 0,
        'total_findings': 0,
        'blockers': [],
        'warnings': [],
        'info': [],
        'findings_by_file': {}
    }
    
    for filepath in root.rglob('*'):
        if not filepath.is_file():
            continue
        
        if not should_scan_file(filepath):
            continue
        
        try:
            # Try UTF-8 first
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try UTF-8 with BOM
                try:
                    with open(filepath, 'r', encoding='utf-8-sig') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # Try Latin-1 as fallback
                    with open(filepath, 'r', encoding='latin-1') as f:
                        content = f.read()
            
            results['files_scanned'] += 1
            
            findings = detect_mojibake(content, filepath)
            
            if findings:
                results['files_with_issues'] += 1
                results['total_findings'] += len(findings)
                
                rel_path = str(filepath.relative_to(root))
                results['findings_by_file'][rel_path] = findings
                
                severity = classify_severity(filepath, findings)
                
                for finding in findings:
                    finding['severity'] = severity
                    if severity == 'BLOCKER':
                        results['blockers'].append(finding)
                    elif severity == 'WARNING':
                        results['warnings'].append(finding)
                    else:
                        results['info'].append(finding)
        
        except Exception as e:
            results['findings_by_file'][str(filepath)] = [{
                'error': str(e),
                'severity': 'INFO'
            }]
    
    results['summary'] = {
        'blocker_count': len(results['blockers']),
        'warning_count': len(results['warnings']),
        'info_count': len(results['info']),
        'verdict': 'BLOCKED' if results['blockers'] else 'PASS' if not results['warnings'] else 'PASS_WITH_WARNINGS'
    }
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Scan for mojibake encoding issues')
    parser.add_argument('--scope', choices=['IMPERIUM_TEST_VERSION', 'FULL_REPO'], 
                        default='IMPERIUM_TEST_VERSION')
    parser.add_argument('--root', help='Root path to scan')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--read-only', action='store_true', 
                        help='Read-only mode for full repo scan')
    
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    
    # Determine root path
    if args.root:
        root_path = Path(args.root)
    else:
        # Auto-detect based on script location
        if args.scope == 'IMPERIUM_TEST_VERSION':
            root_path = script_dir.parent.parent  # AGENT_EXCHANGE -> IMPERIUM_TEST_VERSION
        else:
            root_path = script_dir.parent.parent.parent  # -> IMPERIUM
    
    print(f'Scanning: {root_path}')
    print(f'Scope: {args.scope}')
    
    results = scan_directory(root_path, args.scope)
    
    # Output
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = script_dir.parent / 'REPORTS' / 'latest_mojibake_scan.json'
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f'\nResults saved: {output_path}')
    print(f'Files scanned: {results["files_scanned"]}')
    print(f'Files with issues: {results["files_with_issues"]}')
    print(f'Blockers: {results["summary"]["blocker_count"]}')
    print(f'Warnings: {results["summary"]["warning_count"]}')
    print(f'Verdict: {results["summary"]["verdict"]}')
    
    return 0 if results['summary']['verdict'] != 'BLOCKED' else 1


if __name__ == '__main__':
    sys.exit(main())
