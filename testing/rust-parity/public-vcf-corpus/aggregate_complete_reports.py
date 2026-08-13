#!/usr/bin/env python3
"""Aggregate complete published-artifact coverage for every manifest case."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    expected_cases = [case["id"] for case in manifest["cases"]]
    reports: dict[str, dict[str, object]] = {}
    missing = []
    failed = {}

    for case_id in expected_cases:
        path = args.reports / f"{case_id}.complete.json"
        if not path.is_file():
            missing.append(case_id)
            continue
        report = json.loads(path.read_text())
        reports[case_id] = report
        if not report.get("ok"):
            failed[case_id] = report.get("differences", [])

    all_effective_params_equal = all(
        report.get("provenance", {}).get(
            "effective_params_equal_except_output_and_trace_suffix"
        )
        is True
        for report in reports.values()
    )
    output = {
        "schema_version": 1,
        "manifest_version": manifest["manifest_version"],
        "expected_cases": expected_cases,
        "missing_reports": missing,
        "failed_cases": failed,
        "case_reports": reports,
        "legacy_published_artifacts": sum(
            int(report.get("legacy_published_artifacts", 0))
            for report in reports.values()
        ),
        "rust_published_artifacts": sum(
            int(report.get("rust_published_artifacts", 0))
            for report in reports.values()
        ),
        "semantic_artifacts_compared": sum(
            int(report.get("semantic_artifacts_compared", 0))
            for report in reports.values()
        ),
        "semantic_artifacts_matched": sum(
            int(report.get("semantic_artifacts_matched", 0))
            for report in reports.values()
        ),
        "all_effective_params_equal_except_output_and_trace_suffix": all_effective_params_equal,
        "ok": not missing
        and not failed
        and len(reports) == len(expected_cases)
        and all_effective_params_equal,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "ok": output["ok"],
                "cases": len(reports),
                "missing": missing,
                "semantic_artifacts_compared": output["semantic_artifacts_compared"],
                "semantic_artifacts_matched": output["semantic_artifacts_matched"],
            },
            sort_keys=True,
        )
    )
    return 0 if output["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
