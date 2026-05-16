from pathlib import Path

p = Path("TRUTH_SPINE/truth_aggregator.py")
s = p.read_text(encoding="utf-8")

old_components = '''COMPONENTS = [
    {"id": "smoke", "name": "Smoke Test", "prefix": "RCP-SMOKE"},
    {"id": "mechanicus", "name": "Mechanicus Health", "prefix": "RCP-MECH"},
    {"id": "inquisition", "name": "Inquisition Audit", "prefix": "RCP-INQ"},
    {"id": "master", "name": "Master Verification", "prefix": "RCP-MASTER"},
]'''

new_components = '''BASE_COMPONENTS = [
    {"id": "smoke", "name": "Smoke Test", "prefix": "RCP-SMOKE"},
    {"id": "mechanicus", "name": "Mechanicus Health", "prefix": "RCP-MECH"},
    {"id": "inquisition", "name": "Inquisition Audit", "prefix": "RCP-INQ"},
]

MASTER_COMPONENT = {"id": "master", "name": "Master Verification", "prefix": "RCP-MASTER"}'''

if old_components not in s:
    raise SystemExit("components block not found")

s = s.replace(old_components, new_components)

s = s.replace(
    "def aggregate_truth_state(receipts_dir, threshold_hours=24):",
    "def aggregate_truth_state(receipts_dir, threshold_hours=24, include_master=False):"
)

s = s.replace(
    "    components = []\n    for comp in COMPONENTS:",
    "    components = []\n    selected_components = list(BASE_COMPONENTS)\n    if include_master:\n        selected_components.append(MASTER_COMPONENT)\n\n    for comp in selected_components:"
)

s = s.replace(
    '"source": "truth_aggregator.py"',
    '"source": "truth_aggregator.py",\n        "include_master": include_master,\n        "excluded_components": [] if include_master else ["Master Verification"]'
)

s = s.replace(
    'parser.add_argument("--quiet", action="store_true", help="Suppress detailed output")',
    'parser.add_argument("--quiet", action="store_true", help="Suppress detailed output")\n    parser.add_argument("--include-master", action="store_true", help="Include previous RCP-MASTER receipts. Do not use during RUN_ALL self-run.")'
)

s = s.replace(
    "result = aggregate_truth_state(args.receipts_dir, args.threshold)",
    "result = aggregate_truth_state(args.receipts_dir, args.threshold, include_master=args.include_master)"
)

p.write_text(s, encoding="utf-8")
print("PATCHED_TRUTH_AGGREGATOR_NO_SELF_MASTER")
