$ErrorActionPreference = "Stop"

$env:CORTEX_REQUIRE_GPU = "1"
$env:CORTEX_DEVICE = "cuda"

uv run vuorse-vortex doctor --require-cuda
