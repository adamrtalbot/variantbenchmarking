# Repository instructions

- Build `hap-rs` only from the source commit and Rust toolchain pinned in `Containerfile`.
- Keep the `HAPPY_HAPPY` and `HAPPY_SOMPY` input, output, prefix, and emit contracts unchanged.
- Preserve exact legacy artifact parity; do not weaken comparisons or reduce artifact coverage.
- Public VCF campaign cases must keep germline and somatic analyses separate and use the exact reference build documented in the corpus manifest.
- Do not change any Nextflow process concurrency setting for the public VCF campaign.
- Preserve the existing strict comparator unchanged; add manifest-aware tooling separately.
