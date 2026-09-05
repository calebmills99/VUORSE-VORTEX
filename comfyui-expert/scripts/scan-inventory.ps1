# ComfyUI Inventory Scanner (Offline Mode)
# Scans a ComfyUI install and generates state/inventory.json
#
# Usage: pwsh -File scripts/scan-inventory.ps1 -ComfyUIPath "D:\ComfyUI312\ComfyUI"

param(
    [Parameter(Mandatory = $true)]
    [string]$ComfyUIPath,

    [string]$OutputPath
)

$ErrorActionPreference = "Stop"

if (-not $OutputPath) {
    $OutputPath = Join-Path (Split-Path -Parent (Split-Path -Parent $PSCommandPath)) "state" "inventory.json"
}

Write-Host "ComfyUI Inventory Scanner" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "ComfyUI Path: $ComfyUIPath"
Write-Host "Output:       $OutputPath"
Write-Host ""

if (-not (Test-Path $ComfyUIPath)) {
    Write-Host "[FAIL] ComfyUI path not found: $ComfyUIPath" -ForegroundColor Red
    exit 1
}

$modelsDir      = Join-Path $ComfyUIPath "models"
$customNodesDir = Join-Path $ComfyUIPath "custom_nodes"

if (-not (Test-Path $modelsDir)) {
    Write-Host "[FAIL] No models directory under: $ComfyUIPath" -ForegroundColor Red
    Write-Host "       Is this actually a ComfyUI root?" -ForegroundColor Red
    exit 1
}

# Weight file extensions. Anything not listed here is a sidecar
# (preview .png, .civitai.info, "put_X_here" placeholders) and is skipped.
$weightExt = @(".safetensors", ".ckpt", ".pt", ".pth", ".bin", ".gguf", ".onnx", ".sft")

# Every models/ subdirectory gets scanned. This list only controls display
# order and guarantees a key exists even when the directory is empty.
$knownTypes = @(
    "checkpoints", "diffusion_models", "unet", "loras", "vae", "vae_approx",
    "clip", "clip_vision", "text_encoders", "text-encoders", "controlnet",
    "style_models", "embeddings", "upscale_models", "latent_upscale_models",
    "model_patches", "ipadapter", "instantid", "insightface", "photomaker",
    "facerestore_models", "sams", "detection", "audio_encoders",
    "frame_interpolation", "motion_models", "diffusers", "gligen",
    "hypernetworks", "onnx", "configs"
)

function Get-Weights {
    param([string]$Dir)

    if (-not (Test-Path $Dir)) { return @() }

    $base = (Resolve-Path -LiteralPath $Dir).Path.TrimEnd('\', '/')

    try {
        $found = Get-ChildItem -LiteralPath $Dir -File -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $weightExt -contains $_.Extension.ToLower() }
    } catch {
        Write-Host "  [WARN] Could not read ${Dir}: $($_.Exception.Message)" -ForegroundColor Yellow
        return @()
    }

    $out = @()
    foreach ($f in $found) {
        # Path relative to the type dir, so nested loras stay addressable exactly
        # the way ComfyUI's own dropdowns present them.
        $rel = $f.FullName
        if ($rel.StartsWith($base, [StringComparison]::OrdinalIgnoreCase)) {
            $rel = $rel.Substring($base.Length).TrimStart('\', '/')
        }
        $out += [pscustomobject]@{
            name       = $f.Name
            rel        = $rel
            size_bytes = $f.Length
            size_gb    = [math]::Round($f.Length / 1GB, 2)
        }
    }
    return $out
}

# ---- Environment detection ---------------------------------------------------

# ComfyUI version comes from the build-generated version file.
$comfyVersion = "unknown"
$versionFile  = Join-Path $ComfyUIPath "comfyui_version.py"
if (Test-Path $versionFile) {
    $vMatch = Select-String -LiteralPath $versionFile -Pattern '__version__\s*=\s*"([^"]+)"' -ErrorAction SilentlyContinue
    if ($vMatch) { $comfyVersion = $vMatch.Matches[0].Groups[1].Value }
}

# GPU via nvidia-smi. A missing driver is not fatal -- the offline scan still works.
$gpuName = "unknown"; $vramTotalGb = 0; $vramFreeGb = 0; $computeCap = "unknown"
$smi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($smi) {
    try {
        $q = & nvidia-smi --query-gpu=name,memory.total,memory.free,compute_cap --format=csv,noheader,nounits 2>$null
        if ($LASTEXITCODE -eq 0 -and $q) {
            $parts = ($q | Select-Object -First 1) -split ',' | ForEach-Object { $_.Trim() }
            $gpuName     = $parts[0]
            $vramTotalGb = [math]::Round([double]$parts[1] / 1024, 1)
            $vramFreeGb  = [math]::Round([double]$parts[2] / 1024, 1)
            $computeCap  = $parts[3]
        }
    } catch {
        Write-Host "  [WARN] nvidia-smi query failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Torch build from requirements.txt -- a proxy for what the venv actually has.
$torchBuild = "unknown"
$reqFile = Join-Path $ComfyUIPath "requirements.txt"
if (Test-Path $reqFile) {
    $tMatch = Select-String -LiteralPath $reqFile -Pattern 'torch==(\S+)' -ErrorAction SilentlyContinue
    if ($tMatch) { $torchBuild = $tMatch.Matches[0].Groups[1].Value }
}

$capMajor = -1
if ($computeCap -ne "unknown") {
    $capMajor = [int](($computeCap -split '\.')[0])
}

# NVFP4 needs Blackwell (compute 12.x) AND a cu13x torch build. Recording the
# verdict here means workflow generation never has to re-derive it.
$supportsNvfp4 = ($capMajor -ge 12) -and ($torchBuild -match 'cu13')
$supportsFp8   = ($capMajor -ge 8)

$inventory = [ordered]@{
    last_updated    = (Get-Date -Format "o")
    mode            = "offline"
    comfyui_version = $comfyVersion
    comfyui_path    = $ComfyUIPath
    system          = [ordered]@{
        gpu            = $gpuName
        compute_cap    = $computeCap
        vram_total_gb  = $vramTotalGb
        vram_free_gb   = $vramFreeGb
        torch          = $torchBuild
        supports_fp8   = $supportsFp8
        supports_nvfp4 = $supportsNvfp4
    }
    models          = [ordered]@{}
    model_counts    = [ordered]@{}
    custom_nodes    = @()
    warnings        = @()
}

# ---- Scan models -------------------------------------------------------------

Write-Host "Scanning models (recursive)..." -ForegroundColor Yellow

$presentDirs = @(Get-ChildItem -LiteralPath $modelsDir -Directory -ErrorAction SilentlyContinue |
    ForEach-Object { $_.Name })

# Known types first for stable ordering, then anything else found on disk.
$scanOrder = @()
$scanOrder += $knownTypes | Where-Object { $presentDirs -contains $_ }
$scanOrder += $presentDirs | Where-Object { $knownTypes -notcontains $_ } | Sort-Object

$totalModels = 0
foreach ($type in $scanOrder) {
    $files = @(Get-Weights (Join-Path $modelsDir $type))
    $inventory.models[$type]       = $files
    $inventory.model_counts[$type] = $files.Count
    $totalModels += $files.Count
    if ($files.Count -gt 0) {
        $gb = [math]::Round((($files | Measure-Object -Property size_bytes -Sum).Sum) / 1GB, 1)
        Write-Host ("  {0,-24} {1,4} file(s)  {2,8} GB" -f $type, $files.Count, $gb)
    }
}

# Empty known dirs, reported once and compactly -- they are the usual cause of
# "node is installed but the model is missing" failures.
$emptyKnown = @($knownTypes | Where-Object {
    ($presentDirs -contains $_) -and ($inventory.model_counts[$_] -eq 0)
})
if ($emptyKnown.Count -gt 0) {
    Write-Host ""
    Write-Host "  Empty: $($emptyKnown -join ', ')" -ForegroundColor DarkGray
}

# ---- Scan custom nodes -------------------------------------------------------

Write-Host ""
Write-Host "Scanning custom nodes..." -ForegroundColor Yellow
if (Test-Path $customNodesDir) {
    $nodeDirs = @(Get-ChildItem -LiteralPath $customNodesDir -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ne '__pycache__' -and -not $_.Name.StartsWith('.') } |
        ForEach-Object { $_.Name } |
        Sort-Object)
    $inventory.custom_nodes = $nodeDirs
    Write-Host "  Found: $($inventory.custom_nodes.Count) package(s)"

    # Disabled packages are worth surfacing -- they explain missing node types.
    $disabledDir = Join-Path $customNodesDir ".disabled"
    if (Test-Path $disabledDir) {
        $disabled = @(Get-ChildItem -LiteralPath $disabledDir -Directory -ErrorAction SilentlyContinue |
            ForEach-Object { $_.Name })
        if ($disabled.Count -gt 0) {
            $inventory.warnings += "Disabled custom nodes present: $($disabled -join ', ')"
            Write-Host "  Disabled: $($disabled.Count) package(s)" -ForegroundColor DarkGray
        }
    }
} else {
    $inventory.warnings += "No custom_nodes directory found at $customNodesDir"
    Write-Host "  [WARN] No custom_nodes directory" -ForegroundColor Yellow
}

# ---- Cross-check: node packs installed but their models are missing ----------

$nodeModelDeps = [ordered]@{
    "comfyui_ipadapter_plus" = "ipadapter"
    "comfyui-impact-pack"    = "detection"
}
foreach ($pack in $nodeModelDeps.Keys) {
    $needs = $nodeModelDeps[$pack]
    $have  = 0
    if ($inventory.model_counts.Contains($needs)) { $have = $inventory.model_counts[$needs] }
    if (($inventory.custom_nodes -contains $pack) -and ($have -eq 0)) {
        $inventory.warnings += "'$pack' is installed but models/$needs is empty -- its nodes will fail at runtime."
    }
}

if (-not $supportsNvfp4) {
    $inventory.warnings += "NVFP4 unsupported here (compute $computeCap, torch $torchBuild). Prefer FP8 or GGUF checkpoints."
}

# ---- Write ------------------------------------------------------------------

$outputDir = Split-Path -Parent $OutputPath
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

try {
    $inventory | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
} catch {
    Write-Host "[FAIL] Could not write ${OutputPath}: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Inventory saved to: $OutputPath" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  ComfyUI:      $comfyVersion"
Write-Host "  GPU:          $gpuName ($vramTotalGb GB total, $vramFreeGb GB free, compute $computeCap)"
Write-Host "  Torch:        $torchBuild"
Write-Host "  FP8:          $(if ($supportsFp8)   { 'supported' } else { 'NOT supported' })"
Write-Host "  NVFP4:        $(if ($supportsNvfp4) { 'supported' } else { 'NOT supported' })"
Write-Host "  Total models: $totalModels"
Write-Host "  Custom nodes: $($inventory.custom_nodes.Count)"

if ($inventory.warnings.Count -gt 0) {
    Write-Host ""
    Write-Host "Warnings:" -ForegroundColor Yellow
    foreach ($w in $inventory.warnings) { Write-Host "  - $w" -ForegroundColor Yellow }
}
