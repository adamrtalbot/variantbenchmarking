#!/usr/bin/env python3
"""Aggregate all manifest case reports without relaxing their acceptance rules."""

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
    reports = {}
    missing = []
    for case in manifest["cases"]:
        path = args.reports / f"{case['id']}.json"
        if not path.is_file():
            missing.append(case["id"])
            continue
        reports[case["id"]] = json.loads(path.read_text())
    differences = {
        case_id: report["differences"]
        for case_id, report in reports.items()
        if not report.get("ok")
    }
    output = {
        "schema_version": 1,
        "manifest_version": manifest["manifest_version"],
        "expected_cases": [case["id"] for case in manifest["cases"]],
        "missing_reports": missing,
        "case_reports": reports,
        "total_compared_artifacts": sum(
            report.get("compared_artifacts", 0) for report in reports.values()
        ),
        "total_matched_artifacts": sum(
            report.get("matched_artifacts", 0) for report in reports.values()
        ),
        "differences": differences,
        "ok": not missing and not differences and len(reports) == len(manifest["cases"]),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"ok": output["ok"], "cases": len(reports), "missing": missing}))
    return 0 if output["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
