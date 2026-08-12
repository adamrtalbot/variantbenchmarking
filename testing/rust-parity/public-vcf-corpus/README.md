# Public VCF parity corpus

`manifest.v1.json` is the versioned source of truth for the 2026-08-12
legacy-versus-hap-rs Platform campaign. Every case has a single-row samplesheet
because each matched legacy/Rust pair has its own truth set, reference, work
prefix, result prefix, and clean-run audit.

The source VCFs, indexes, truth sets, regions, and compressed reference bundles
were downloaded in full and SHA-256 checked before inclusion. The manifest also
records observed samples, contigs, and complete `bcftools stats` variant counts.
References are staged as uncompressed FASTA plus FAI under the campaign S3
prefix; their checksums are the decompressed checksums recorded in the manifest.

Run `compare_manifest_case.py` after downloading a matched output pair. It loads
the unchanged `compare_outputs.py`, supplies the manifest case's expected sample
and artifact count, and writes the normal strict comparison report. Run
`aggregate_reports.py` only after all six per-case reports exist.
