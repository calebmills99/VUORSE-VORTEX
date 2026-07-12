$ErrorActionPreference = "Stop"

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Path
)

uv run vuorse-vortex validate-jsonl $Path
