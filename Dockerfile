# VUORSE-VORTEX Docker image
# GPU-first with CUDA 12.x base for Vast.ai deployment

FROM nvidia/cuda:12.4.1-cudnn9-runtime-ubuntu22.04

# ── System dependencies ────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-dev \
    python3-pip \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# ── Install UV ─────────────────────────────────────────────────────────────
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# ── Working directory ──────────────────────────────────────────────────────
WORKDIR /app

# ── Copy project files ─────────────────────────────────────────────────────
COPY pyproject.toml ./
COPY src/ ./src/
COPY manifests/ ./manifests/

# ── Install dependencies ───────────────────────────────────────────────────
RUN uv sync --no-dev

# ── Environment defaults ───────────────────────────────────────────────────
ENV VORTEX_LOG_FORMAT=json \
    VORTEX_LOG_LEVEL=INFO \
    VORTEX_REQUIRE_CUDA=true \
    VORTEX_VECTOR_BACKEND=chromadb

# ── Entrypoint ─────────────────────────────────────────────────────────────
ENTRYPOINT ["uv", "run", "vortex"]
CMD ["--help"]

# ── Health check ───────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run vortex gpu-status || exit 1

LABEL maintainer="VUORSE-VORTEX Contributors" \
      description="Anti-erasure cognition architecture for the Slayverse universe" \
      version="0.1.0"
