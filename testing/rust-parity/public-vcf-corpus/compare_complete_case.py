#!/usr/bin/env python3
"""Compare every published parity artifact and account for provenance outputs."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
import re


PROVENANCE_PATTERNS = {
    "execution_report": re.compile(r"execution_report_.*\.html$"),
    "execution_trace": re.compile(r"execution_trace_.*\.txt$"),
    "manifest": re.compile(r"manifest_.*\.bco\.json$"),
    "params": re.compile(r"params_.*\.json$"),
    "pipeline_dag": re.compile(r"pipeline_dag_.*\.html$"),
    "software_versions": re.compile(r"nf_core_variantbenchmarking_software_mqc_versions\.yml$"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparator", type=Path, required=True)
    parser.add_argument("--legacy", type=Path, required=True)
    parser.add_argument("--rust", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def load_comparator(path: Path):
    spec = importlib.util.spec_from_file_location("strict_compare_outputs", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load comparator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def published_files(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file()
    }


def provenance_category(relative: str) -> str | None:
    if not relative.startswith("pipeline_info/"):
        return None
    name = Path(relative).name
    return next(
        (category for category, pattern in PROVENANCE_PATTERNS.items() if pattern.fullmatch(name)),
        "unknown",
    )


def provenance_inventory(files: dict[str, Path]) -> dict[str, list[dict[str, object]]]:
    inventory = {category: [] for category in PROVENANCE_PATTERNS}
    inventory["unknown"] = []
    for relative, path in sorted(files.items()):
        category = provenance_category(relative)
        if category is not None:
            inventory[category].append({"artifact": relative, "bytes": path.stat().st_size})
    return inventory


def comparable_params(path: Path) -> dict[str, object]:
    value = copy.deepcopy(json.loads(path.read_text()))
    value.pop("outdir", None)
    value.pop("trace_report_suffix", None)
    return value


def main() -> int:
    args = parse_args()
    comparator = load_comparator(args.comparator)
    legacy = published_files(args.legacy)
    rust = published_files(args.rust)
    legacy_parity = {name: path for name, path in legacy.items() if provenance_category(name) is None}
    rust_parity = {name: path for name, path in rust.items() if provenance_category(name) is None}

    differences: list[dict[str, object]] = []
    missing = sorted(set(legacy_parity) - set(rust_parity))
    unexpected = sorted(set(rust_parity) - set(legacy_parity))
    if missing or unexpected:
        differences.append({"kind": "artifact_set", "missing": missing, "unexpected": unexpected})

    artifact_results = []
    for relative in sorted(set(legacy_parity).intersection(rust_parity)):
        difference = comparator.compare_artifact(
            relative, legacy_parity[relative], rust_parity[relative]
        )
        artifact_results.append({"artifact": relative, "matched": difference is None})
        if difference is not None:
            differences.append(difference)

    legacy_provenance = provenance_inventory(legacy)
    rust_provenance = provenance_inventory(rust)
    provenance_differences = []
    for category in sorted(set(legacy_provenance).union(rust_provenance)):
        legacy_count = len(legacy_provenance.get(category, []))
        rust_count = len(rust_provenance.get(category, []))
        if legacy_count != rust_count or category == "unknown" and legacy_count:
            provenance_differences.append({
                "category": category,
                "legacy_count": legacy_count,
                "rust_count": rust_count,
            })

    legacy_params = [path for name, path in legacy.items() if provenance_category(name) == "params"]
    rust_params = [path for name, path in rust.items() if provenance_category(name) == "params"]
    params_equal = (
        len(legacy_params) == len(rust_params) == 1
        and comparable_params(legacy_params[0]) == comparable_params(rust_params[0])
    )
    if not params_equal:
        provenance_differences.append({"category": "params", "reason": "effective parameters differ after removing only outdir"})
    if provenance_differences:
        differences.append({"kind": "provenance_coverage", "details": provenance_differences})

    compared = len(artifact_results)
    matched = sum(item["matched"] for item in artifact_results)
    report = {
        "schema_version": 1,
        "ok": not differences,
        "legacy_published_artifacts": len(legacy),
        "rust_published_artifacts": len(rust),
        "semantic_artifacts_compared": compared,
        "semantic_artifacts_matched": matched,
        "artifact_results": artifact_results,
        "differences": differences,
        "provenance": {
            "legacy": legacy_provenance,
            "rust": rust_provenance,
        "effective_params_equal_except_output_and_trace_suffix": params_equal,
            "policy": {
                "execution_report": "presence and size recorded; contains implementation-specific runtime telemetry",
                "execution_trace": "presence and size recorded; task telemetry is extracted separately",
                "manifest": "presence and size recorded; intentionally identifies different pinned implementations",
                "params": "JSON compared after removing only outdir and the generated trace_report_suffix",
                "pipeline_dag": "presence and size recorded; generated identifiers and timestamps are implementation-specific",
                "software_versions": "presence and size recorded; implementation provenance is expected to differ",
            },
        },
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "ok": report["ok"],
        "semantic_artifacts_compared": compared,
        "semantic_artifacts_matched": matched,
        "legacy_published_artifacts": len(legacy),
        "rust_published_artifacts": len(rust),
    }, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
