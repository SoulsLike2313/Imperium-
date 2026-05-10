from pathlib import Path
import re

source = Path(r"E:\IMPERIUM\EXPLORER\imperium_explorer_v0_5.py")
if not source.exists():
    source = Path(r"E:\IMPERIUM\EXPLORER\imperium_explorer_v0_4.py")

target = Path(r"E:\IMPERIUM\EXPLORER\imperium_explorer_v0_6.py")
readme = Path(r"E:\IMPERIUM\EXPLORER\README.md")
changelog = Path(r"E:\IMPERIUM\EXPLORER\CHANGELOG.md")

code = source.read_text(encoding="utf-8", errors="replace")

code = re.sub(
    r'APP_NAME\s*=\s*"[^"]*"',
    'APP_NAME = "IMPERIUM Explorer V0.6 Truth Aligned"',
    code,
)

# 1. Inject ARCHIVE_COLD_STORAGE classification directly after IMPERIUM_ROOT.
if 'return "ARCHIVE_COLD_STORAGE"' not in code:
    code = code.replace(
        '        if name == "IMPERIUM":\n            return "IMPERIUM_ROOT"\n',
        '        if name == "IMPERIUM":\n'
        '            return "IMPERIUM_ROOT"\n'
        '        if name in {"ARCHIVE", "_ARCHIVE", "IMPERIUM_ARCHIVE"}:\n'
        '            return "ARCHIVE_COLD_STORAGE"\n'
    )

# 2. Add visual tree tag.
if 'tag_configure("ARCHIVE_COLD_STORAGE"' not in code:
    code = code.replace(
        '        self.tree.tag_configure("EXPLORER_ROOT", foreground="#4de4b0")\n',
        '        self.tree.tag_configure("EXPLORER_ROOT", foreground="#4de4b0")\n'
        '        self.tree.tag_configure("ARCHIVE_COLD_STORAGE", foreground="#8a8a8a")\n'
    )

# 3. Add details panel archive policy block.
if 'ARCHIVE_POLICY: COLD_STORAGE_TOP_LEVEL_ONLY' not in code:
    code = code.replace(
        '        lines.append(f"TYPE: {node_type}")\n',
        '        lines.append(f"TYPE: {node_type}")\n'
        '        if node_type == "ARCHIVE_COLD_STORAGE":\n'
        '            lines.append("ARCHIVE_POLICY: COLD_STORAGE_TOP_LEVEL_ONLY")\n'
        '            lines.append("ARCHIVE_RECURSIVE_SCAN: DISABLED")\n'
        '            lines.append("ARCHIVE_ACTIVE_PROCESS: FALSE")\n'
    )

target.write_text(code, encoding="utf-8")

with changelog.open("a", encoding="utf-8") as f:
    f.write("""

## V0.6

STATUS: ARCHIVE_TRUTH_ALIGNMENT_REPAIR

Changed:
- created imperium_explorer_v0_6.py;
- forces ARCHIVE / _ARCHIVE / IMPERIUM_ARCHIVE to display as ARCHIVE_COLD_STORAGE;
- adds archive policy lines to details panel;
- keeps Explorer read-only.

Launch:
python E:\\IMPERIUM\\EXPLORER\\imperium_explorer_v0_6.py

""")

with readme.open("a", encoding="utf-8") as f:
    f.write("""

Current truth-aligned candidate:
- imperium_explorer_v0_6.py

Launch truth-aligned candidate:
python E:\\IMPERIUM\\EXPLORER\\imperium_explorer_v0_6.py

""")

print("PASS: created", target)
print("Launch:")
print(r"python E:\IMPERIUM\EXPLORER\imperium_explorer_v0_6.py")
