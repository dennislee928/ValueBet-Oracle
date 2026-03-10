# ValueBet Oracle - Rust Gateway (多階段建置縮小映像)
FROM rust:1.75-bookworm AS builder
WORKDIR /build
COPY Cargo.toml ./
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates libssl3 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /build/target/release/valuebet-gateway /usr/local/bin/
EXPOSE 3000
CMD ["valuebet-gateway"]
