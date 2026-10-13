# GPU Runtime Policy

Use GPU for deep-learning workloads.

```bash
export CORTEX_REQUIRE_GPU=1
export CORTEX_DEVICE=cuda
```

CPU is acceptable for validation and small diagnostics only.

## Sanctioned cloud provisioner

To materialize a host that satisfies this policy by construction, use
`scripts/vast_provision.py`. It pre-bakes `CORTEX_REQUIRE_GPU=1` and
`CORTEX_DEVICE=cuda` into the launched container and refuses shapes below the
VUORSE floor (≥32 GB VRAM, ≥500 GB disk, reliability > 0.99, North America).
Dry-run by default; pass `--launch` to spend.

```bash
uv run scripts/vast_provision.py                          # dry-run
uv run scripts/vast_provision.py --launch --commit-hours 720
```
