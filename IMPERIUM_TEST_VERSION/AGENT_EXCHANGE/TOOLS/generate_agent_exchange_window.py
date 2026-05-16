#!/usr/bin/env python3
"""
GENERATE AGENT EXCHANGE WINDOW
Creates HTML dashboard for agent communication flow.

Usage:
    py -3 generate_agent_exchange_window.py [--exchange-root AGENT_EXCHANGE]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AGENT EXCHANGE WINDOW</title>
    <style>
        :root {{
            --bg-dark: #1a1a2e;
            --bg-card: #16213e;
            --accent-gold: #d4af37;
            --accent-green: #00ff88;
            --accent-red: #ff4444;
            --accent-yellow: #ffaa00;
            --accent-blue: #4488ff;
            --text-primary: #e8e8e8;
            --text-secondary: #a0a0a0;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            padding: 20px;
            border-bottom: 2px solid var(--accent-gold);
            margin-bottom: 20px;
        }}
        .header h1 {{
            color: var(--accent-gold);
            font-size: 1.8em;
            margin-bottom: 10px;
        }}
        .scope-badge {{
            background: var(--accent-gold);
            color: var(--bg-dark);
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
        }}
        .meta {{
            color: var(--text-secondary);
            margin-top: 10px;
            font-size: 0.9em;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }}
        .card {{
            background: var(--bg-card);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid #333;
        }}
        .card h2 {{
            color: var(--accent-gold);
            font-size: 1.1em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #333;
        }}
        .thread-item {{
            background: #1e2a4a;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid var(--accent-blue);
        }}
        .thread-item.active {{
            border-left-color: var(--accent-green);
        }}
        .thread-item.waiting {{
            border-left-color: var(--accent-yellow);
        }}
        .thread-item.blocked {{
            border-left-color: var(--accent-red);
        }}
        .thread-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }}
        .thread-id {{
            font-family: monospace;
            color: var(--accent-blue);
        }}
        .thread-status {{
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.8em;
        }}
        .status-active {{ background: var(--accent-green); color: var(--bg-dark); }}
        .status-waiting {{ background: var(--accent-yellow); color: var(--bg-dark); }}
        .status-blocked {{ background: var(--accent-red); color: white; }}
        .status-completed {{ background: #666; color: white; }}
        .inbox-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px;
            border-bottom: 1px solid #333;
        }}
        .inbox-item:last-child {{ border-bottom: none; }}
        .agent-name {{
            font-weight: bold;
        }}
        .agent-kiro {{ color: var(--accent-blue); }}
        .agent-servitor {{ color: var(--accent-green); }}
        .agent-logos {{ color: var(--accent-gold); }}
        .agent-owner {{ color: var(--accent-yellow); }}
        .message-flow {{
            font-family: monospace;
            font-size: 0.85em;
            background: #0a0a1a;
            padding: 15px;
            border-radius: 5px;
            max-height: 300px;
            overflow-y: auto;
        }}
        .flow-item {{
            padding: 5px 0;
            border-bottom: 1px solid #222;
        }}
        .flow-arrow {{
            color: var(--accent-gold);
        }}
        .evidence-list {{
            font-family: monospace;
            font-size: 0.85em;
        }}
        .evidence-item {{
            padding: 5px 0;
            word-break: break-all;
        }}
        .action-panel {{
            text-align: center;
            padding: 20px;
        }}
        .action-btn {{
            background: var(--bg-card);
            border: 2px solid var(--accent-gold);
            color: var(--accent-gold);
            padding: 10px 20px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
        }}
        .action-btn:hover {{
            background: var(--accent-gold);
            color: var(--bg-dark);
        }}
        .display-only {{
            font-size: 0.7em;
            color: var(--text-secondary);
            display: block;
            margin-top: 5px;
        }}
        .next-action {{
            background: var(--accent-gold);
            color: var(--bg-dark);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
        }}
        footer {{
            text-align: center;
            padding: 20px;
            color: var(--text-secondary);
            font-size: 0.8em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📬 AGENT EXCHANGE WINDOW</h1>
        <div class="scope-badge">SCOPE: IMPERIUM_TEST_VERSION ONLY</div>
        <div class="meta">
            Generated: {generated_at}<br>
            Repo HEAD: {repo_head}<br>
            Exchange Status: {exchange_status}
        </div>
    </div>

    <div class="grid">
        <!-- Active Thread -->
        <div class="card">
            <h2>🧵 Active Thread</h2>
            {thread_html}
        </div>

        <!-- Inbox Status -->
        <div class="card">
            <h2>📥 Inbox Status</h2>
            {inbox_html}
        </div>

        <!-- Message Flow -->
        <div class="card" style="grid-column: 1 / -1;">
            <h2>📨 Message Flow Timeline</h2>
            <div class="message-flow">
                {flow_html}
            </div>
        </div>

        <!-- Evidence -->
        <div class="card">
            <h2>📋 Evidence Paths</h2>
            <div class="evidence-list">
                {evidence_html}
            </div>
        </div>

        <!-- Required Action -->
        <div class="card">
            <h2>⚡ Required Action</h2>
            <div class="next-action">
                {next_action}
            </div>
            <div style="margin-top: 15px; font-size: 0.9em;">
                <strong>Who should act:</strong> {next_agent}<br>
                <strong>File to read:</strong> <code>{file_to_read}</code><br>
                <strong>Output path:</strong> <code>{output_path}</code>
            </div>
        </div>

        <!-- Owner Panel -->
        <div class="card" style="grid-column: 1 / -1;">
            <h2>👤 Owner Panel</h2>
            <p style="margin-bottom: 15px;">
                <strong>What to open:</strong> {owner_open}<br>
                <strong>What to verify:</strong> {owner_verify}<br>
                <strong>What NOT to trust yet:</strong> {owner_not_trust}
            </p>
            <div class="action-panel">
                <button class="action-btn" onclick="alert('Open: {delta_window_path}')">
                    🔍 Open Delta Window
                    <span class="display-only">DISPLAY_ONLY_MVP</span>
                </button>
                <button class="action-btn" onclick="alert('Read: {kiro_bundle_path}')">
                    📦 View Kiro Bundle
                    <span class="display-only">DISPLAY_ONLY_MVP</span>
                </button>
                <button class="action-btn" onclick="alert('Read: {servitor_bundle_path}')">
                    📋 View Servitor Advice
                    <span class="display-only">DISPLAY_ONLY_MVP</span>
                </button>
            </div>
        </div>
    </div>

    <footer>
        AGENT EXCHANGE WINDOW R1<br>
        Scope: IMPERIUM_TEST_VERSION only | Buttons are DISPLAY_ONLY<br>
        This window shows agent communication flow, not active execution.
    </footer>
</body>
</html>
'''


def read_json_safe(path):
    """Read JSON file safely."""
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except:
        return None


def find_latest_thread(exchange_root):
    """Find the latest/active thread."""
    threads_dir = exchange_root / 'THREADS'
    if not threads_dir.exists():
        return None
    
    threads = list(threads_dir.iterdir())
    if not threads:
        return None
    
    # Sort by name (includes date)
    threads.sort(key=lambda x: x.name, reverse=True)
    return threads[0]


def count_inbox(exchange_root, agent):
    """Count messages in agent's inbox."""
    inbox = exchange_root / 'INBOX' / agent
    if not inbox.exists():
        return 0
    return len(list(inbox.glob('*.json'))) + len(list(inbox.glob('*.md')))


def generate_window(exchange_root, repo_root):
    """Generate Agent Exchange Window HTML."""
    exchange_root = Path(exchange_root)
    repo_root = Path(repo_root)
    
    # Read exchange state
    state_path = exchange_root / 'EXCHANGE_STATE.json'
    state = read_json_safe(state_path) or {}
    
    # Read latest exchange status
    status_path = exchange_root / 'REPORTS' / 'latest_exchange_status.json'
    status = read_json_safe(status_path) or {}
    
    # Find active thread
    thread_dir = find_latest_thread(exchange_root)
    thread_index = None
    if thread_dir:
        index_path = thread_dir / 'thread_index.json'
        thread_index = read_json_safe(index_path)
    
    # Get git HEAD
    import subprocess
    try:
        head = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            cwd=repo_root, capture_output=True, text=True
        ).stdout.strip()
    except:
        head = 'unknown'
    
    # Build thread HTML
    if thread_index:
        thread_status = thread_index.get('status', 'UNKNOWN')
        status_class = {
            'ACTIVE': 'active',
            'WAITING': 'waiting',
            'BLOCKED': 'blocked'
        }.get(thread_status, '')
        
        thread_html = f'''
        <div class="thread-item {status_class}">
            <div class="thread-header">
                <span class="thread-id">{thread_index.get('thread_id', 'unknown')}</span>
                <span class="thread-status status-{status_class or 'active'}">{thread_status}</span>
            </div>
            <div><strong>Topic:</strong> {thread_index.get('topic', 'unknown')}</div>
            <div><strong>Participants:</strong> {', '.join(thread_index.get('participants', []))}</div>
            <div><strong>Next expected:</strong> {thread_index.get('next_expected_agent', 'unknown')}</div>
            <div><strong>Owner decision:</strong> {'YES' if thread_index.get('owner_decision_required') else 'NO'}</div>
        </div>
        '''
    else:
        thread_html = '<div class="thread-item">No active thread found</div>'
    
    # Build inbox HTML
    inbox_html = ''
    for agent in ['KIRO', 'SERVITOR', 'LOGOS_PRIME', 'OWNER_REVIEW']:
        count = count_inbox(exchange_root, agent)
        agent_class = f'agent-{agent.lower().split("_")[0]}'
        inbox_html += f'''
        <div class="inbox-item">
            <span class="agent-name {agent_class}">{agent}</span>
            <span>{count} message(s)</span>
        </div>
        '''
    
    # Build flow HTML
    flow_html = ''
    if thread_index and 'messages' in thread_index:
        for msg in thread_index.get('messages', []):
            flow_html += f'''
            <div class="flow-item">
                <span class="agent-name agent-{msg.get('from', 'unknown').lower()}">{msg.get('from', '?')}</span>
                <span class="flow-arrow"> → </span>
                <span class="agent-name agent-{msg.get('to', 'unknown').lower()}">{msg.get('to', '?')}</span>
                : {msg.get('type', 'message')} ({msg.get('status', 'unknown')})
            </div>
            '''
    else:
        # Default flow based on current state
        flow_html = '''
        <div class="flow-item">
            <span class="agent-name agent-servitor">SERVITOR</span>
            <span class="flow-arrow"> → </span>
            <span class="agent-name agent-kiro">KIRO</span>
            : ADVICE_BUNDLE (DELIVERED)
        </div>
        <div class="flow-item">
            <span class="agent-name agent-kiro">KIRO</span>
            <span class="flow-arrow"> → </span>
            <span>?</span>
            : RESPONSE_BUNDLE (PENDING)
        </div>
        '''
    
    # Build evidence HTML
    evidence_paths = [
        'AGENT_EXCHANGE/EXCHANGE_STATE.json',
        'AGENT_EXCHANGE/REPORTS/latest_exchange_status.json',
        'TESTING_FIELD/DELTA_WINDOW/delta_window.html',
        'TESTING_FIELD/DELTA_WINDOW/REPORTS/latest_delta_report.json'
    ]
    if thread_dir:
        evidence_paths.append(f'AGENT_EXCHANGE/THREADS/{thread_dir.name}/thread_index.json')
    
    evidence_html = '\n'.join(f'<div class="evidence-item">📄 {p}</div>' for p in evidence_paths)
    
    # Determine next action
    next_agent = thread_index.get('next_expected_agent', 'KIRO') if thread_index else 'KIRO'
    
    if next_agent == 'KIRO':
        next_action = 'KIRO must read Servitor advice and produce response bundle'
        file_to_read = 'AGENT_EXCHANGE/THREADS/.../SERVITOR_TO_KIRO_ADVICE_BUNDLE.json'
        output_path = 'AGENT_EXCHANGE/OUTBOX/KIRO/KIRO_RESPONSE_BUNDLE_*.md'
    elif next_agent == 'SERVITOR':
        next_action = 'SERVITOR must audit Kiro work and produce audit report'
        file_to_read = 'AGENT_EXCHANGE/OUTBOX/KIRO/KIRO_RESPONSE_BUNDLE_*.md'
        output_path = 'AUDITS/SERVITOR_*_AUDIT/AUDIT_REPORT.md'
    else:
        next_action = f'{next_agent} must act next'
        file_to_read = 'See thread index'
        output_path = 'See protocol'
    
    return HTML_TEMPLATE.format(
        generated_at=datetime.now(timezone.utc).isoformat(),
        repo_head=head,
        exchange_status=state.get('status', 'UNKNOWN'),
        thread_html=thread_html,
        inbox_html=inbox_html,
        flow_html=flow_html,
        evidence_html=evidence_html,
        next_action=next_action,
        next_agent=next_agent,
        file_to_read=file_to_read,
        output_path=output_path,
        owner_open='Delta Window HTML, Agent Exchange Window HTML',
        owner_verify='Precommit verdict, evidence paths exist',
        owner_not_trust='Screenshots (may be blocked), historical comparisons (partial)',
        delta_window_path='TESTING_FIELD/DELTA_WINDOW/delta_window.html',
        kiro_bundle_path='AGENT_EXCHANGE/OUTBOX/KIRO/KIRO_RESPONSE_BUNDLE_*.md',
        servitor_bundle_path='AGENT_EXCHANGE/THREADS/.../SERVITOR_TO_KIRO_ADVICE_BUNDLE.md'
    )


def main():
    parser = argparse.ArgumentParser(description='Generate Agent Exchange Window')
    parser.add_argument('--exchange-root', help='Agent Exchange root path')
    parser.add_argument('--repo-root', help='Repository root')
    parser.add_argument('--output', help='Output HTML path')
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    
    if args.exchange_root:
        exchange_root = Path(args.exchange_root)
    else:
        exchange_root = script_dir.parent  # TOOLS -> AGENT_EXCHANGE
    
    if args.repo_root:
        repo_root = Path(args.repo_root)
    else:
        repo_root = exchange_root.parent.parent  # AGENT_EXCHANGE -> IMPERIUM_TEST_VERSION -> IMPERIUM
    
    html = generate_window(exchange_root, repo_root)
    
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = exchange_root / 'agent_exchange_window.html'
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f'Agent Exchange Window generated: {output_path}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
