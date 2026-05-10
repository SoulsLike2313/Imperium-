import json
from pathlib import Path
from datetime import datetime

ROOT = Path(r"E:\IMPERIUM\SSH_COMMAND_LIBRARY")

def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

index = {
    "library_id": "IMPERIUM_SSH_COMMAND_LIBRARY",
    "status": "TESTED_WORKING",
    "created_for": "MetaOS-Imperium / Sanctum button backend",
    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "purpose": "Store tested SSH/SCP routes, scripts, recipes, and machine-readable contracts for PC <-> VM3 handoff.",
    "canonical_warning": "Operational evidence only. Not THRONE. Not admission.",
    "root_path": str(ROOT),
    "known_vm3_connection": {
        "user": "vboxuser3",
        "host": "127.0.0.1",
        "port": 2225,
        "identity_file": r"C:\Users\PC\.ssh\imperium_pc_to_vm3_ed25519_20260418",
        "status": "TESTED_OK"
    },
    "routes": [
        {
            "route_id": "PC_TO_VM3_PROMPT_HANDOFF",
            "status": "TESTED_OK",
            "entrypoint": r"06_TOOLS\PC_TO_VM3_PROMPT_HANDOFF\SEND_LATEST_DRAFT_TO_VM3.py",
            "helper": r"06_TOOLS\PC_TO_VM3_PROMPT_HANDOFF\send_prompt_to_vm3.py",
            "pc_source": r"E:\IMPERIUM\PROMPT_OUTBOX_TO_VM3\00_DRAFTS",
            "pc_ready": r"E:\IMPERIUM\PROMPT_OUTBOX_TO_VM3\01_READY_TO_SEND",
            "pc_sent": r"E:\IMPERIUM\PROMPT_OUTBOX_TO_VM3\02_SENT",
            "pc_receipts": r"E:\IMPERIUM\PROMPT_OUTBOX_TO_VM3\03_RECEIPTS",
            "vm3_target": "/home/vboxuser3/Desktop/IMPERIUM_STAGING/bridge_exchange/current_task_inputs",
            "contract": "Latest draft txt becomes step folder with PROMPT.txt on VM3, then opens on VM3 for manual copy into Codex/Servik.",
            "verification": "sha256 local/remote match"
        },
        {
            "route_id": "VM3_TO_PC_FETCH_LATEST_BUNDLE",
            "status": "TESTED_OK",
            "entrypoint": r"06_TOOLS\VM3_TO_PC_FETCH_BUNDLE\fetch_latest_vm3_bundle.py",
            "vm3_source": "/home/vboxuser3/Desktop/IMPERIUM_STAGING/bridge_exchange/current_task_outputs",
            "pc_target": r"E:\IMPERIUM\PC_OWNER_TEST_BENCH\00_INBOX_FROM_VM3",
            "pc_receipts": r"E:\IMPERIUM\PC_OWNER_TEST_BENCH\04_RECEIPTS",
            "contract": "Fetch latest zip bundle from VM3 current_task_outputs to PC inbox, verify sha256, open PC inbox.",
            "verification": "sha256 remote/local match"
        }
    ],
    "safety_rules": [
        "No private key contents.",
        "No API keys, passwords, tokens, cookies, or credentials.",
        "No delete.",
        "No cleanup.",
        "No admission.",
        "No THRONE mutation.",
        "PC is review/test bench only.",
        "VM3 staging folders are exchange surfaces only."
    ]
}

write_json(ROOT / "00_MACHINE_README.json", index)

readme = """# IMPERIUM SSH Command Library

Status: TESTED_WORKING

Purpose:
This folder stores tested SSH/SCP routes, scripts, recipes, and machine-readable contracts for PC <-> VM3 handoff.

Start here:
1. 00_MACHINE_README.json
2. 06_TOOLS/*/TOOL_MANIFEST.json
3. 05_SUCCESSFUL_RECIPES/

Main routes:

## PC_TO_VM3_PROMPT_HANDOFF

Entrypoint:
06_TOOLS\\PC_TO_VM3_PROMPT_HANDOFF\\SEND_LATEST_DRAFT_TO_VM3.py

Purpose:
Take latest .txt draft from:
E:\\IMPERIUM\\PROMPT_OUTBOX_TO_VM3\\00_DRAFTS

Send it to VM3 as:
current_task_inputs/<STEP_ID>/PROMPT.txt

Then open PROMPT.txt on VM3 for manual copy into Codex/Servik.

## VM3_TO_PC_FETCH_LATEST_BUNDLE

Entrypoint:
06_TOOLS\\VM3_TO_PC_FETCH_BUNDLE\\fetch_latest_vm3_bundle.py

Purpose:
Fetch latest .zip bundle from VM3 current_task_outputs to:
E:\\IMPERIUM\\PC_OWNER_TEST_BENCH\\00_INBOX_FROM_VM3

Then verify sha256 and open the PC inbox.

Safety:
- This library does not perform admission.
- This library does not mutate THRONE.
- This library does not make PC canonical.
- This library must not contain secrets.
"""

write_text(ROOT / "README_AGENT.md", readme)

prompt_manifest = {
    "tool_group_id": "PC_TO_VM3_PROMPT_HANDOFF",
    "status": "TESTED_OK",
    "entrypoint": "SEND_LATEST_DRAFT_TO_VM3.py",
    "helper": "send_prompt_to_vm3.py",
    "input": r"E:\IMPERIUM\PROMPT_OUTBOX_TO_VM3\00_DRAFTS\*.txt",
    "output_pc_ready": r"E:\IMPERIUM\PROMPT_OUTBOX_TO_VM3\01_READY_TO_SEND\<STEP_ID>\PROMPT.txt",
    "output_pc_sent": r"E:\IMPERIUM\PROMPT_OUTBOX_TO_VM3\02_SENT\<STEP_ID>\PROMPT.txt",
    "output_pc_receipt": r"E:\IMPERIUM\PROMPT_OUTBOX_TO_VM3\03_RECEIPTS\<STEP_ID>.receipt.txt",
    "output_vm3": "/home/vboxuser3/Desktop/IMPERIUM_STAGING/bridge_exchange/current_task_inputs/<STEP_ID>/PROMPT.txt",
    "opens_on_vm3": True,
    "verification": "sha256 local/remote match",
    "run_command": r'python "E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\PC_TO_VM3_PROMPT_HANDOFF\SEND_LATEST_DRAFT_TO_VM3.py"',
    "forbidden": ["secrets", "admission", "delete", "cleanup", "canon mutation"]
}

fetch_manifest = {
    "tool_group_id": "VM3_TO_PC_FETCH_LATEST_BUNDLE",
    "status": "TESTED_OK",
    "entrypoint": "fetch_latest_vm3_bundle.py",
    "input_vm3": "/home/vboxuser3/Desktop/IMPERIUM_STAGING/bridge_exchange/current_task_outputs/*.zip",
    "output_pc": r"E:\IMPERIUM\PC_OWNER_TEST_BENCH\00_INBOX_FROM_VM3",
    "output_pc_receipt": r"E:\IMPERIUM\PC_OWNER_TEST_BENCH\04_RECEIPTS",
    "opens_on_pc": True,
    "verification": "sha256 remote/local match",
    "run_command": r'python "E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\VM3_TO_PC_FETCH_BUNDLE\fetch_latest_vm3_bundle.py"',
    "forbidden": ["delete remote files", "admission", "cleanup", "canon mutation"]
}

write_json(ROOT / "06_TOOLS" / "PC_TO_VM3_PROMPT_HANDOFF" / "TOOL_MANIFEST.json", prompt_manifest)
write_json(ROOT / "06_TOOLS" / "VM3_TO_PC_FETCH_BUNDLE" / "TOOL_MANIFEST.json", fetch_manifest)

print("DONE")
print("Wrote:")
print(ROOT / "00_MACHINE_README.json")
print(ROOT / "README_AGENT.md")
print(ROOT / "06_TOOLS" / "PC_TO_VM3_PROMPT_HANDOFF" / "TOOL_MANIFEST.json")
print(ROOT / "06_TOOLS" / "VM3_TO_PC_FETCH_BUNDLE" / "TOOL_MANIFEST.json")