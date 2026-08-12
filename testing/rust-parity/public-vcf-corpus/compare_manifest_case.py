#!/usr/bin/env python3
"""Run the preserved strict comparator with one manifest case's coverage contract."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--comparator", type=Path, required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--legacy", type=Path, required=True)
    parser.add_argument("--rust", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(args.manifest.read_text())
    cases = {case["id"]: case for case in manifest["cases"]}
    if args.case_id not in cases:
        raise ValueError(f"case not found in manifest: {args.case_id}")
    case = cases[args.case_id]

    spec = importlib.util.spec_from_file_location("strict_compare_outputs", args.comparator)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load comparator: {args.comparator}")
    comparator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(comparator)

    lane = case["analysis"]
    comparator.LANES[lane] = {
        "variant_type": "small",
        "tool": "happy" if lane == "germline" else "sompy",
        "sample_ids": {args.case_id},
        "primary_per_sample": 11 if lane == "germline" else 3,
    }
    sys.argv = [
        str(args.comparator),
        "--lane", lane,
        "--legacy", str(args.legacy),
        "--rust", str(args.rust),
        "--report", str(args.report),
    ]
    return comparator.main()


if __name__ == "__main__":
    raise SystemExit(main())
