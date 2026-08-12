#!/usr/bin/env python3
"""Create pinned per-case Platform parameters for one implementation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--corpus-commit", required=True)
    parser.add_argument("--implementation", choices=("legacy", "rust"), required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    launches = []
    for case in manifest["cases"]:
        reference = manifest["references"][case["reference"]]
        truth = manifest["truth_sets"][case["truth_set"]]
        tool = "happy" if case["analysis"] == "germline" else "sompy"
        params = {
            "input": (
                "https://raw.githubusercontent.com/adamrtalbot/variantbenchmarking/"
                f"{args.corpus_commit}/testing/rust-parity/public-vcf-corpus/"
                f"{case['samplesheet']}"
            ),
            "outdir": f"{args.prefix}/{case['id']}/{args.implementation}/results",
            "fasta": reference["campaign_fasta"],
            "fai": reference["campaign_fai"],
            "analysis": case["analysis"],
            "variant_type": "small",
            "method": tool,
            "preprocess": case.get(
                "preprocess", "split_multiallelic,normalize,deduplicate"
            ),
            "truth_id": truth["sample"].split("/")[0].split(" ")[0],
            "truth_vcf": truth["vcf"],
            "regions_bed": truth["regions"],
            "skip_plots": "metrics,upset,svlength",
            "igenomes_ignore": True,
            "high_conf": True,
            "publish_dir_mode": "copy"
        }
        params_path = args.output_dir / f"{case['id']}-{args.implementation}.params.json"
        params_path.write_text(json.dumps(params, indent=2, sort_keys=True) + "\n")
        launches.append({
            "case_id": case["id"],
            "analysis": case["analysis"],
            "implementation": args.implementation,
            "params_file": params_path.name,
            "work_dir": f"{args.prefix}/{case['id']}/{args.implementation}/work",
            "run_name": f"vb-public-{case['id']}-{args.implementation}-20260812",
            "resume": False
        })
    output = {
        "manifest_version": manifest["manifest_version"],
        "corpus_commit": args.corpus_commit,
        "implementation": args.implementation,
        "launches": launches
    }
    (args.output_dir / f"launches-{args.implementation}.json").write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
