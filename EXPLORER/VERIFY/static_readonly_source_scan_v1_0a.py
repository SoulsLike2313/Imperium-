from pathlib import Path
from datetime import datetime
import json
import re

SOURCE = Path(r"E:\IMPERIUM\EXPLORER\imperium_explorer_v1_0a.py")
OUT_ROOT = Path(r"E:\IMPERIUM\EXPLORER\VERIFY")
OUT_ROOT.mkdir(parents=True, exist_ok=True)

FORBIDDEN_PATTERNS = {
    "write_text": r"\.write_text\s*\(",
    "open_write_mode": r"open\s*\([^)]*[\"']w[\"']",
    "unlink": r"\.unlink\s*\(",
    "remove": r"os\.remove\s*\(",
    "rmdir": r"os\.rmdir\s*\(",
    "shutil_move": r"shutil\.move\s*\(",
    "shutil_copy": r"shutil\.copy",
    "requests": r"\brequests\b",
    "urllib": r"\burllib\b",
    "socket": r"\bsocket\b",
    "paramiko": r"\bparamiko\b",
    "watchdog": r"\bwatchdog\b",
    "threading": r"\bthreading\b",
    "multiprocessing": r"\bmultiprocessing\b"
}

ALLOWED_UI_SIDE_EFFECTS = [
    "clipboard_copy_path",
    "subprocess.Popen(['explorer', ...]) for Open in Explorer"
]

def main():
    text = SOURCE.read_text(encoding="utf-8", errors="replace")
    findings = []

    for name, pattern in FORBIDDEN_PATTERNS.items():
        matches = list(re.finditer(pattern, text))
        if matches:
            findings.append({
                "severity": "BLOCKER",
                "pattern_id": name,
                "matches_count": len(matches)
            })

    verdict = "PASS_STATIC_READ_ONLY_SCAN"
    if findings:
        verdict = "BLOCKED_STATIC_READ_ONLY_SCAN_FINDINGS"

    report = {
        "scan_name": "EXPLORER_V1_0A_STATIC_READ_ONLY_SOURCE_SCAN",
        "created_at_local": datetime.now().isoformat(timespec="seconds"),
        "source": str(SOURCE),
        "allowed_ui_side_effects": ALLOWED_UI_SIDE_EFFECTS,
        "forbidden_patterns_checked": list(FORBIDDEN_PATTERNS.keys()),
        "findings": findings,
        "verdict": verdict
    }

    json_path = OUT_ROOT / "EXPLORER_V1_0A_STATIC_READ_ONLY_SCAN_REPORT.json"
    md_path = OUT_ROOT / "EXPLORER_V1_0A_STATIC_READ_ONLY_SCAN_REPORT.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Explorer V1.0A Static Read-Only Source Scan",
        "",
        f"Source: `{SOURCE}`",
        f"Verdict: `{verdict}`",
        "",
        "## Allowed UI side effects",
        ""
    ]

    for item in ALLOWED_UI_SIDE_EFFECTS:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("## Findings")
    lines.append("")

    if findings:
        for item in findings:
            lines.append(f"- `{item['severity']}` `{item['pattern_id']}` count=`{item['matches_count']}`")
    else:
        lines.append("- none")

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print("Static read-only scan complete.")
    print("Verdict:", verdict)
    print("JSON:", json_path)
    print("MD:", md_path)

if __name__ == "__main__":
    main()
