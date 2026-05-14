import argparse
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ALLOWED_PRESENTATION_PARTS = {
    "I18N",
    "i18n",
    "LOCALIZATION",
    "localization",
}

ALLOWED_POLICY_FILES = {
    "IMPERIUM_CANONICAL_LANGUAGE_AND_UI_LOCALIZATION_POLICY_V0_1.md",
}

def has_cyrillic(text: str) -> bool:
    for ch in text:
        code = ord(ch)
        if 0x0400 <= code <= 0x052F:
            return True
    return False

def is_allowed_presentation_path(path: Path) -> bool:
    parts = set(path.parts)
    if path.name in ALLOWED_POLICY_FILES:
        return True
    return bool(parts.intersection(ALLOWED_PRESENTATION_PARTS))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths", nargs="+", required=True)
    args = parser.parse_args()

    checked = 0
    violations = []

    for raw in args.paths:
        root = Path(raw)
        if not root.exists():
            violations.append({"path": str(root), "issue": "missing_path"})
            continue

        files = [root] if root.is_file() else list(root.rglob("*"))

        for path in files:
            if not path.is_file():
                continue
            if path.suffix.lower() not in [".json", ".md", ".txt", ".yaml", ".yml", ".py", ".html", ".css", ".js"]:
                continue

            checked += 1

            try:
                text = path.read_text(encoding="utf-8-sig")
            except Exception as exc:
                violations.append({"path": str(path), "issue": "utf8_decode_failure", "detail": repr(exc)})
                continue

            if has_cyrillic(text) and not is_allowed_presentation_path(path):
                violations.append({
                    "path": str(path),
                    "issue": "cyrillic_in_canonical_artifact",
                    "policy": "Russian is allowed only in live chat or approved i18n/presentation paths."
                })

    status = "PASS" if not violations else "BLOCKED"

    print(json.dumps({
        "status": status,
        "checked_files": checked,
        "violations": violations[:100]
    }, ensure_ascii=True, indent=2))

    return 0 if status == "PASS" else 2

if __name__ == "__main__":
    sys.exit(main())
