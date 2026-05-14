import argparse, json, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def emit(status, message, **kw):
    print(json.dumps({"status": status, "message": message, **kw}, ensure_ascii=True, indent=2))
    sys.exit(0 if status == "PASS" else 2)

p = argparse.ArgumentParser()
p.add_argument("--paths", nargs="+", required=True)
a = p.parse_args()

# Runtime patterns are real mojibake markers, but source code stores them as escapes
# so the guard does not flag itself.
patterns = [
    "\u0432\u0402", "\u0432\u201e",
    "\u0420\u040f", "\u0420\u0153", "\u0420\u00bd", "\u0420\u0455",
    "\u0421\u201a", "\u0421\u0451", "\u00d0", "\u00d1", "\ufffd"
]

skip_names = {
    "bootstrap_astronomicon_missing_gates_v0_1.py",
    "repair_astronomicon_guard_false_blocks_v0_1.py"
}

bad = []
count = 0

for root in a.paths:
    rootp = Path(root)
    if not rootp.exists():
        continue
    for f in rootp.rglob("*"):
        if not f.is_file():
            continue
        if f.name in skip_names:
            continue
        if f.suffix.lower() not in [".md", ".json", ".html", ".py", ".txt", ".yaml", ".yml", ".css", ".js"]:
            continue

        count += 1
        try:
            txt = f.read_text(encoding="utf-8")
        except Exception as e:
            bad.append({"file": str(f), "issue": "decode_failure", "detail": repr(e)})
            continue

        hits = [pat.encode("unicode_escape").decode("ascii") for pat in patterns if pat in txt]
        if hits:
            bad.append({"file": str(f), "issue": "mojibake_pattern", "hits": hits[:10]})

if bad:
    emit("BLOCKED", "utf8/mojibake guard failed", file_count=count, bad=bad[:100])

emit("PASS", "utf8/mojibake guard passed", file_count=count)
