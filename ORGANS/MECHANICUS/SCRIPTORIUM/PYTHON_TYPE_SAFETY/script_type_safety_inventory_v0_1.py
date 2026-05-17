from __future__ import annotations

import ast
import json
import py_compile
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

STRICT_STATUS_SENTINEL = "STRICT_STATUS_NOT_MEASURED_BY_PYLANCE"

REPO_ROOT = Path(__file__).resolve().parents[4]
REPORT_JSON_PATH = REPO_ROOT / "ORGANS/ADMINISTRATUM/REPORTS/SCRIPT_TYPE_SAFETY_INVENTORY_V0_1.json"
REPORT_MD_PATH = REPO_ROOT / "ORGANS/ADMINISTRATUM/REPORTS/SCRIPT_TYPE_SAFETY_INVENTORY_V0_1.md"

SCRIPT_CANDIDATES = [
    "ORGANS/MECHANICUS/SCRIPTORIUM/GATE_RUNNERS/imperium_gate_pack_builder_v0_1.py",
    "ORGANS/MECHANICUS/SCRIPTORIUM/GATE_RUNNERS/imperium_gate_receipt_check_v0_1.py",
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/visual_performance_receipt_runner_v0_1.py",
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/visual_fake_green_scanner_v0_1.py",
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/browser_performance_audit_runner_v0_1.py",
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/full_runtime_performance_audit_runner_v0_1.py",
]


@dataclass
class ScriptInventoryRow:
    script_path: str
    exists: bool
    line_count: int
    py_compile_status: str
    py_compile_error: Optional[str]
    function_definitions: int
    functions_with_return_annotations: int
    parameters_total: int
    parameters_with_annotations: int
    occurrences_any: int
    occurrences_type_ignore: int
    occurrences_noqa: int
    occurrences_broad_except_exception: int
    json_load_calls: int
    json_dump_calls: int
    pathlib_or_path_string_operations: int
    strict_status: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_head() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=REPO_ROOT,
                text=True,
                stderr=subprocess.DEVNULL,
            )
            .strip()
        )
    except Exception:
        return "UNKNOWN_HEAD"


def compile_status(path: Path) -> tuple[str, Optional[str]]:
    try:
        py_compile.compile(str(path), doraise=True)
        return "PASS", None
    except py_compile.PyCompileError as exc:
        return "FAIL", str(exc)
    except Exception as exc:
        return "FAIL", repr(exc)


def count_parameters(function_node: ast.AST) -> tuple[int, int]:
    if not isinstance(function_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return 0, 0
    args = function_node.args
    positional = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
    extra = [arg for arg in (args.vararg, args.kwarg) if arg is not None]
    all_args = positional + extra
    total = len(all_args)
    annotated = sum(1 for arg in all_args if arg.annotation is not None)
    return total, annotated


def analyze_script(path: Path, rel_path: str) -> ScriptInventoryRow:
    if not path.exists():
        return ScriptInventoryRow(
            script_path=rel_path,
            exists=False,
            line_count=0,
            py_compile_status="MISSING",
            py_compile_error="FILE_NOT_FOUND",
            function_definitions=0,
            functions_with_return_annotations=0,
            parameters_total=0,
            parameters_with_annotations=0,
            occurrences_any=0,
            occurrences_type_ignore=0,
            occurrences_noqa=0,
            occurrences_broad_except_exception=0,
            json_load_calls=0,
            json_dump_calls=0,
            pathlib_or_path_string_operations=0,
            strict_status=STRICT_STATUS_SENTINEL,
        )

    content = path.read_text(encoding="utf-8")
    lines = content.count("\n") + 1
    pyc_status, pyc_error = compile_status(path)

    function_defs = 0
    functions_with_return = 0
    params_total = 0
    params_annotated = 0
    json_load_calls = 0
    json_dump_calls = 0

    try:
        tree = ast.parse(content, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_defs += 1
                if node.returns is not None:
                    functions_with_return += 1
                total, annotated = count_parameters(node)
                params_total += total
                params_annotated += annotated
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "json":
                    if node.func.attr == "load":
                        json_load_calls += 1
                    if node.func.attr == "dump":
                        json_dump_calls += 1
    except SyntaxError:
        pass

    occurrences_any = len(re.findall(r"\bAny\b", content))
    occurrences_type_ignore = len(re.findall(r"type:\s*ignore", content))
    occurrences_noqa = len(re.findall(r"\bnoqa\b", content, flags=re.IGNORECASE))
    occurrences_broad_except = len(re.findall(r"except\s+Exception\b", content))
    path_ops = 0
    path_ops += len(re.findall(r"\bPath\(", content))
    path_ops += len(re.findall(r"\bpathlib\.", content))
    path_ops += len(re.findall(r"\bos\.path\.", content))
    path_ops += len(re.findall(r"\bresolve\(", content))

    return ScriptInventoryRow(
        script_path=rel_path,
        exists=True,
        line_count=lines,
        py_compile_status=pyc_status,
        py_compile_error=pyc_error,
        function_definitions=function_defs,
        functions_with_return_annotations=functions_with_return,
        parameters_total=params_total,
        parameters_with_annotations=params_annotated,
        occurrences_any=occurrences_any,
        occurrences_type_ignore=occurrences_type_ignore,
        occurrences_noqa=occurrences_noqa,
        occurrences_broad_except_exception=occurrences_broad_except,
        json_load_calls=json_load_calls,
        json_dump_calls=json_dump_calls,
        pathlib_or_path_string_operations=path_ops,
        strict_status=STRICT_STATUS_SENTINEL,
    )


def build_markdown(report: dict) -> str:
    lines = []
    lines.append("# SCRIPT TYPE SAFETY INVENTORY V0.1")
    lines.append("")
    lines.append(f"- generated_at: `{report['generated_at']}`")
    lines.append(f"- current_head: `{report['current_head']}`")
    lines.append(f"- strict_status: `{report['strict_status']}`")
    lines.append("- note: strict status is not measured by Pylance/Pyright in this script.")
    lines.append("")
    lines.append("| Script | Compile | defs | return ann | param ann | Any | type:ignore | noqa | broad except | json load/dump | path ops |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row in report["candidates"]:
        param_ratio = f"{row['parameters_with_annotations']}/{row['parameters_total']}"
        load_dump = f"{row['json_load_calls']}/{row['json_dump_calls']}"
        lines.append(
            f"| `{row['script_path']}` | {row['py_compile_status']} | {row['function_definitions']} | {row['functions_with_return_annotations']} | {param_ratio} | {row['occurrences_any']} | {row['occurrences_type_ignore']} | {row['occurrences_noqa']} | {row['occurrences_broad_except_exception']} | {load_dump} | {row['pathlib_or_path_string_operations']} |"
        )
    lines.append("")
    lines.append("## Summary")
    summary = report["summary"]
    lines.append(f"- total_scripts: `{summary['total_scripts']}`")
    lines.append(f"- compile_pass: `{summary['compile_pass']}`")
    lines.append(f"- compile_fail_or_missing: `{summary['compile_fail_or_missing']}`")
    lines.append(f"- strict_status: `{summary['strict_status']}`")
    return "\n".join(lines) + "\n"


def main() -> int:
    rows = []
    for rel_path in SCRIPT_CANDIDATES:
        abs_path = REPO_ROOT / rel_path
        rows.append(analyze_script(abs_path, rel_path))

    row_dicts = [asdict(row) for row in rows]
    compile_pass = sum(1 for row in rows if row.py_compile_status == "PASS")
    compile_fail_or_missing = sum(1 for row in rows if row.py_compile_status != "PASS")

    report = {
        "task_id": "TASK-MECHANICUS-SCRIPTORIUM-PYTHON-TYPE-SAFETY-INVENTORY-V0_1",
        "generated_at": utc_now_iso(),
        "current_head": git_head(),
        "strict_status": STRICT_STATUS_SENTINEL,
        "source_context": [
            "ORGANS/MECHANICUS/SCRIPTORIUM/PYTHON_TYPE_SAFETY/SCRIPT_TYPE_SAFETY_POLICY_V0_1.md",
            "ORGANS/MECHANICUS/SCRIPTORIUM/PYTHON_TYPE_SAFETY/SCRIPT_TYPE_SAFETY_BACKLOG_V0_1.json"
        ],
        "candidates": row_dicts,
        "summary": {
            "total_scripts": len(rows),
            "compile_pass": compile_pass,
            "compile_fail_or_missing": compile_fail_or_missing,
            "strict_status": STRICT_STATUS_SENTINEL
        },
        "status": "INVENTORY_GENERATED"
    }

    REPORT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD_PATH.write_text(build_markdown(report), encoding="utf-8")

    print("INVENTORY_JSON", REPORT_JSON_PATH)
    print("INVENTORY_MD", REPORT_MD_PATH)
    print("STRICT_STATUS", STRICT_STATUS_SENTINEL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
