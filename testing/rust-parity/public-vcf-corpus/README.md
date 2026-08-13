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

The Ultima case opts into `fix_format_cardinality` before the common
preprocessing sequence. Its source declares `BG_SB` and `SB` as `Number=R` even
though each allele stores a forward/reverse pair. The step corrects those two
header declarations to variable cardinality and preserves every VCF record.

Run `compare_manifest_case.py` after downloading a matched output pair. It loads
the unchanged `compare_outputs.py`, supplies the manifest case's expected sample
and artifact count, and writes the normal strict comparison report. Run
`compare_complete_case.py` to account for every published artifact, including
implementation-specific provenance outputs. Run `aggregate_reports.py` and
`aggregate_complete_reports.py` only after all six corresponding per-case
reports exist.
