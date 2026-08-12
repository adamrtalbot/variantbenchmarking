FROM --platform=linux/amd64 docker.io/library/rust@sha256:c9ac3fa8945b61dede1e4500d25028aa8fd8a8fe46365fcf9c0422f8d999b9b0 AS builder

ARG HAP_RS_REPOSITORY=https://github.com/adamrtalbot/hap.py.git
ARG HAP_RS_COMMIT=f662d6afbad572a022ffaaa44d7d282317a5315e

WORKDIR /src
RUN git init \
    && git remote add origin "${HAP_RS_REPOSITORY}" \
    && git fetch --depth 1 origin "${HAP_RS_COMMIT}" \
    && git checkout --detach FETCH_HEAD \
    && test "$(git rev-parse HEAD)" = "${HAP_RS_COMMIT}" \
    && cargo build --locked --release --bin hap

FROM --platform=linux/amd64 docker.io/library/debian@sha256:362e64223cc0da95422b3b13c045186fc0a81250e765d31c025fbddf257f6143

LABEL org.opencontainers.image.title="hap-rs" \
      org.opencontainers.image.description="Rust implementation of hap.py for nf-core/variantbenchmarking" \
      org.opencontainers.image.source="https://github.com/adamrtalbot/hap.py" \
      org.opencontainers.image.revision="f662d6afbad572a022ffaaa44d7d282317a5315e" \
      org.opencontainers.image.version="0.1.0" \
      io.seqera.variantbenchmarking.rust-version="1.89.0"

RUN apt-get update \
    && apt-get install --yes --no-install-recommends procps \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /src/target/release/hap /usr/local/bin/hap
