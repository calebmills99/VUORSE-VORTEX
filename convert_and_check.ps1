$ErrorActionPreference = "Stop"

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$LegacyJsonl,
    [Parameter(Position = 1)]
    [string]$CleanJsonl = "cleaned.jsonl"
)

if (-not (Test-Path -LiteralPath $LegacyJsonl -PathType Leaf)) {
    Write-Error "Error: file not found -> $LegacyJsonl"
    exit 1
}

uv run vuorse-vortex convert-jsonl $LegacyJsonl --output $CleanJsonl

Write-Host "[INFO] Conversion finished. Running firewall validation ..."
try {
    uv run vuorse-vortex firewall $CleanJsonl
}
catch {
    Write-Host "[ERROR] Firewall validation failed - see the messages above."
    exit 1
}

Write-Host "[SUCCESS] All records passed the canon firewall."
