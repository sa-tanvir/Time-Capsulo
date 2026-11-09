# Era toolchain for Rust repos (2017-2019): rustc/cargo 1.40.0 (Dec 2019)
# Registry cache and target dirs live on named volumes (see benchmark/repos/rust__*.json).
# Base image pinned by digest (checked on 2026-10-20 to be the exact base of the images used for all published results).
FROM rust:1.40-slim@sha256:6e05c9a5249e671a7675aaad2eb25cd2815810bc73fb858b749fa59942b0062d
ENV CARGO_INCREMENTAL=0 \
    CARGO_NET_OFFLINE=false \
    RUSTFLAGS="-C debuginfo=0"
WORKDIR /w
