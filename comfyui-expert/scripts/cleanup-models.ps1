<#
.SYNOPSIS
    Reports (and optionally fixes) duplicate and misfiled models in a ComfyUI install.
.DESCRIPTION
    DRY RUN BY DEFAULT. Nothing is moved or deleted unless -Execute is passed, and
    -Execute additionally requires -Confirm to guard against a stray keystroke.

    Three categories are reported:

      DUPLICATE  Byte-identical copies of the same weights in two locations. The copy
                 inside a node-pack-specific directory (FlashVSR/, SEEDVR2/) or the
                 architecturally correct directory is KEPT; the stray copy is removed.

      MISFILED   Files sitting in checkpoints/ that are not checkpoints -- VLMs, VAEs,
                 upscaler components, projection layers. These pollute the
                 CheckpointLoaderSimple dropdown and mislead workflow generation.
                 These are MOVED, never deleted.

      UNUSABLE   Weights this GPU cannot execute (currently: NVFP4 on pre-Blackwell).

    Duplicate detection is hash-verified, not name+size guessed. By default a sampled
    hash (first 16MB + last 16MB + length) is used, which is decisive for safetensors
    and GGUF. Pass -FullHash to hash entire files instead -- correct but slow, since it
    reads every candidate end to end.
.EXAMPLE
    pwsh -File scripts/cleanup-models.ps1 -ComfyUIPath "D:\ComfyUI312\ComfyUI"
    pwsh -File scripts/cleanup-models.ps1 -ComfyUIPath "D:\ComfyUI312\ComfyUI" -FullHash
    pwsh -File scripts/cleanup-models.ps1 -ComfyUIPath "D:\ComfyUI312\ComfyUI" -Execute -Confirm
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$ComfyUIPath,

    [switch]$Execute,
    [switch]$Confirm,
    [switch]$FullHash,

    # Where MISFILED files get moved to, relative to models/.
    [string]$QuarantineDir = "_misfiled"
)

$ErrorActionPreference = "Stop"

if ($Execute -and -not $Confirm) {
    Write-Host "[REFUSED] -Execute requires -Confirm as well." -ForegroundColor Red
    Write-Host "          Re-run with both flags once you have read the dry-run output." -ForegroundColor Red
    exit 1
}

$modelsDir = Join-Path $ComfyUIPath "models"
if (-not (Test-Path $modelsDir)) {
    Write-Host "[FAIL] No models directory under: $ComfyUIPath" -ForegroundColor Red
    exit 1
}

$mode = if ($Execute) { "EXECUTE" } else { "DRY RUN" }
Write-Host "ComfyUI Model Cleanup" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host "Path: $modelsDir"
Write-Host "Mode: $mode" -ForegroundColor $(if ($Execute) { "Red" } else { "Yellow" })
Write-Host "Hash: $(if ($FullHash) { 'full file' } else { 'sampled (16MB head + 16MB tail + length)' })"
Write-Host ""

# ---- Hashing -----------------------------------------------------------------

function Get-SampledHash {
    param([string]$Path)

    $sample = 16MB
    $fs = $null
    try {
        $fs = [System.IO.File]::OpenRead($Path)
        $sha = [System.Security.Cryptography.SHA256]::Create()
        $len = $fs.Length

        if ($len -le ($sample * 2)) {
            $bytes = New-Object byte[] $len
            [void]$fs.Read($bytes, 0, $len)
            $hash = $sha.ComputeHash($bytes)
        } else {
            $head = New-Object byte[] $sample
            [void]$fs.Read($head, 0, $sample)

            $tail = New-Object byte[] $sample
            [void]$fs.Seek(-$sample, [System.IO.SeekOrigin]::End)
            [void]$fs.Read($tail, 0, $sample)

            $lenBytes = [BitConverter]::GetBytes($len)
            $combined = New-Object byte[] ($sample * 2 + $lenBytes.Length)
            [Array]::Copy($head, 0, $combined, 0, $sample)
            [Array]::Copy($tail, 0, $combined, $sample, $sample)
            [Array]::Copy($lenBytes, 0, $combined, $sample * 2, $lenBytes.Length)
            $hash = $sha.ComputeHash($combined)
        }
        return [BitConverter]::ToString($hash).Replace("-", "")
    } catch {
        Write-Host "  [WARN] Could not hash ${Path}: $($_.Exception.Message)" -ForegroundColor Yellow
        return $null
    } finally {
        if ($fs) { $fs.Dispose() }
    }
}

function Get-Digest {
    param([string]$Path)
    if ($FullHash) {
        try {
            return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
        } catch {
            Write-Host "  [WARN] Could not hash ${Path}: $($_.Exception.Message)" -ForegroundColor Yellow
            return $null
        }
    }
    return Get-SampledHash -Path $Path
}

# ---- Which copy of a duplicate pair wins --------------------------------------

# Deciding which copy to delete is the only genuinely dangerous judgement this script
# makes, so it only auto-deletes where the answer is unambiguous and defers everything
# else to the operator. Three rules fire, in order; if none apply the group is REVIEW.
#
#   Rule 1  One copy sits in a node pack's own model dir (FlashVSR/, SEEDVR2/, LLM/)
#           and the other is loose in checkpoints/. The node reads its own directory;
#           the checkpoints/ copy is a stray that also pollutes the checkpoint dropdown.
#           -> keep the node-pack copy.
#
#   Rule 2  One filename carries a "(N)" download-collision marker. Config files and
#           saved workflows reference the clean name.
#           -> keep the clean name.
#
#   Rule 3  The file is a known non-checkpoint (see $misfileMap) sitting in checkpoints/
#           while a copy exists in its correct directory.
#           -> keep the correctly-filed copy.
#
# Deliberately NOT a rule: "checkpoints/ vs diffusion_models/ for a real model". Both
# are legitimate load paths depending on whether the file is all-in-one or UNET-only,
# and guessing wrong silently breaks saved workflows. Those become REVIEW.

$nodePackDirs = @('FlashVSR', 'SEEDVR2', 'LLM')

function Get-TopDir {
    param([string]$FullPath, [string]$Root)
    return (($FullPath.Substring($Root.Length).TrimStart('\','/')) -split '[\\/]')[0]
}

function Test-HasCollisionMarker {
    param([string]$Name)
    # Matches "foo (2).safetensors" / "foo(2).safetensors" -- browser and copy markers.
    return $Name -match '\s*\(\d+\)\s*\.[A-Za-z0-9]+$'
}

function Resolve-DuplicateGroup {
    param([array]$Group, [string]$Root)

    $inNodePack = @($Group | Where-Object { $nodePackDirs -contains (Get-TopDir $_.FullName $Root) })
    $inCheckpoints = @($Group | Where-Object { (Get-TopDir $_.FullName $Root) -eq 'checkpoints' })

    # Rule 1
    if ($inNodePack.Count -eq 1 -and $inCheckpoints.Count -eq ($Group.Count - 1)) {
        return @{ Keep = $inNodePack[0]; Reason = 'node pack loads from its own directory' }
    }

    # Rule 2
    $clean = @($Group | Where-Object { -not (Test-HasCollisionMarker $_.Name) })
    $marked = @($Group | Where-Object { Test-HasCollisionMarker $_.Name })
    if ($clean.Count -eq 1 -and $marked.Count -gt 0) {
        return @{ Keep = $clean[0]; Reason = 'other copy has a "(N)" download-collision marker' }
    }

    # Rule 3 -- the checkpoints/ copy of a known non-checkpoint is always the stray,
    # however many correctly-filed copies exist elsewhere. Only the stray is dropped.
    if ($inCheckpoints.Count -ge 1 -and $inCheckpoints.Count -lt $Group.Count) {
        $allMisfiled = @($inCheckpoints | Where-Object { $misfileMap.ContainsKey($_.Name) })
        if ($allMisfiled.Count -eq $inCheckpoints.Count) {
            $other = @($Group | Where-Object { (Get-TopDir $_.FullName $Root) -ne 'checkpoints' })
            if ($other.Count -ge 1) {
                return @{
                    Keep    = $other[0]
                    KeepAll = $other
                    Reason  = 'not a checkpoint; correctly-filed copy already exists'
                }
            }
        }
    }

    return $null   # ambiguous -> REVIEW
}

# ---- Classification of misfiled checkpoints -----------------------------------

# Files in checkpoints/ that are not base checkpoints, and where they belong.
$misfileMap = @{
    'Florence_2_large_model.safetensors'              = 'LLM'
    'molmo-7B-D-bnb-4bit.safetensors'                 = 'LLM'
    'Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ2_M.gguf' = 'LLM'
    'ema_vae_fp16.safetensors'                        = 'vae'
    'Wan2.1_VAE.safetensors'                          = 'vae'
    'TCDecoder.safetensors'                           = 'FlashVSR'
    'LQ_proj_in.safetensors'                          = 'FlashVSR'
    'Wan2_1_FlashVSR_LQ_proj_model_bf16.safetensors'  = 'FlashVSR'
    'FlashVSR1_1.safetensors'                         = 'FlashVSR'
    'seedvr2_ema_3b_fp16.safetensors'                 = 'SEEDVR2'
    'seedvr2_ema_3b_fp8_e4m3fn.safetensors'           = 'SEEDVR2'
    'seedvr2_ema_7b_fp8_e4m3fn.safetensors'           = 'SEEDVR2'
    'Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors' = 'loras'
    'Prompt.safetensors'                              = 'REVIEW'
}

# Weights this GPU cannot run. Populated from the inventory's capability flags.
$unusablePatterns = @('nvfp4')

# ---- Scan --------------------------------------------------------------------

$weightExt = @(".safetensors", ".ckpt", ".pt", ".pth", ".bin", ".gguf")

Write-Host "Scanning..." -ForegroundColor Yellow
$all = @(Get-ChildItem -LiteralPath $modelsDir -File -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $weightExt -contains $_.Extension.ToLower() -and $_.Length -gt 10MB })
Write-Host "  $($all.Count) weight files over 10MB"
Write-Host ""

# Only hash files whose (length) collides -- no point hashing unique sizes.
$bySize = $all | Group-Object Length | Where-Object { $_.Count -gt 1 }
Write-Host "Hash-verifying $(($bySize | Measure-Object -Property Count -Sum).Sum) size-collision candidates..." -ForegroundColor Yellow

$dupGroups = @()
foreach ($g in $bySize) {
    $digests = @{}
    foreach ($f in $g.Group) {
        $d = Get-Digest -Path $f.FullName
        if (-not $d) { continue }
        if (-not $digests.ContainsKey($d)) { $digests[$d] = @() }
        $digests[$d] += $f
    }
    foreach ($k in $digests.Keys) {
        if ($digests[$k].Count -gt 1) { $dupGroups += ,$digests[$k] }
    }
}
Write-Host "  $($dupGroups.Count) confirmed duplicate group(s)"
Write-Host ""

# ---- Plan --------------------------------------------------------------------

$plan = @()

foreach ($group in $dupGroups) {
    $decision = Resolve-DuplicateGroup -Group $group -Root $modelsDir

    if ($null -eq $decision) {
        # Ambiguous: both locations are legitimate load paths. Report, never delete.
        $paths = ($group | ForEach-Object { $_.FullName.Substring($modelsDir.Length).TrimStart('\','/') }) -join '  |  '
        $plan += [pscustomobject]@{
            Category = 'DUPLICATE'
            Action   = 'REVIEW'
            Path     = $group[0].FullName
            Detail   = "identical copies, both locations valid -- you pick: $paths"
            Bytes    = $group[0].Length
        }
        continue
    }

    $keep = $decision.Keep
    $keepRel = $keep.FullName.Substring($modelsDir.Length).TrimStart('\','/')
    # KeepAll lets a rule protect several siblings at once (e.g. drop only the
    # checkpoints/ stray while leaving every correctly-filed copy in place).
    $keepSet = if ($decision.KeepAll) { @($decision.KeepAll | ForEach-Object { $_.FullName }) } else { @($keep.FullName) }
    foreach ($drop in @($group | Where-Object { $keepSet -notcontains $_.FullName })) {
        $plan += [pscustomobject]@{
            Category = 'DUPLICATE'
            Action   = 'DELETE'
            Path     = $drop.FullName
            Detail   = "identical to $keepRel -- keeping that one because $($decision.Reason)"
            Bytes    = $drop.Length
        }
    }
}

# Any path the duplicate pass already ruled on -- deleted OR deferred to review -- is
# off-limits to the misfiled and unusable passes. Otherwise one file gets two verdicts.
$plannedDeletes = @($plan | ForEach-Object { $_.Path })

$checkpointsDir = Join-Path $modelsDir "checkpoints"
foreach ($f in @($all | Where-Object { $_.DirectoryName -eq $checkpointsDir })) {
    if ($plannedDeletes -contains $f.FullName) { continue }   # already being removed
    if ($misfileMap.ContainsKey($f.Name)) {
        $dest = $misfileMap[$f.Name]
        if ($dest -eq 'REVIEW') {
            $plan += [pscustomobject]@{
                Category = 'MISFILED'; Action = 'REVIEW'; Path = $f.FullName
                Detail = "unrecognised - inspect manually, not a base checkpoint"; Bytes = $f.Length
            }
        } else {
            $plan += [pscustomobject]@{
                Category = 'MISFILED'; Action = 'MOVE'; Path = $f.FullName
                Detail = "-> models/$dest/"; Bytes = $f.Length
            }
        }
    }
}

foreach ($f in $all) {
    if ($plannedDeletes -contains $f.FullName) { continue }
    foreach ($pat in $unusablePatterns) {
        if ($f.Name -match $pat) {
            $plan += [pscustomobject]@{
                Category = 'UNUSABLE'; Action = 'DELETE'; Path = $f.FullName
                Detail = "NVFP4 requires Blackwell + cu130; this GPU is compute 8.9 / cu128"
                Bytes = $f.Length
            }
        }
    }
}

# ---- Report ------------------------------------------------------------------

if ($plan.Count -eq 0) {
    Write-Host "Nothing to do -- no duplicates, misfiled, or unusable models found." -ForegroundColor Green
    exit 0
}

foreach ($cat in @('DUPLICATE', 'MISFILED', 'UNUSABLE')) {
    $items = @($plan | Where-Object { $_.Category -eq $cat })
    if ($items.Count -eq 0) { continue }

    $catBytes = ($items | Where-Object { $_.Action -eq 'DELETE' } | Measure-Object -Property Bytes -Sum).Sum
    $suffix = if ($catBytes) { " -- $([math]::Round($catBytes/1GB,1)) GB reclaimable" } else { "" }
    Write-Host "$cat ($($items.Count))$suffix" -ForegroundColor Cyan

    foreach ($i in ($items | Sort-Object -Property Bytes -Descending)) {
        $rel = $i.Path.Substring($modelsDir.Length).TrimStart('\','/')
        $colour = switch ($i.Action) { 'DELETE' { 'Red' } 'MOVE' { 'Yellow' } default { 'Gray' } }
        Write-Host ("  {0,-7} {1,7:N1} GB  {2}" -f $i.Action, ($i.Bytes/1GB), $rel) -ForegroundColor $colour
        Write-Host ("                          {0}" -f $i.Detail) -ForegroundColor DarkGray
    }
    Write-Host ""
}

$totalReclaim = ($plan | Where-Object { $_.Action -eq 'DELETE' } | Measure-Object -Property Bytes -Sum).Sum
Write-Host "Total reclaimable: $([math]::Round($totalReclaim/1GB,1)) GB" -ForegroundColor Cyan
Write-Host ""

if (-not $Execute) {
    Write-Host "DRY RUN -- nothing was changed." -ForegroundColor Yellow
    Write-Host "Re-run with -Execute -Confirm to apply." -ForegroundColor Yellow
    exit 0
}

# ---- Execute -----------------------------------------------------------------

Write-Host "Applying..." -ForegroundColor Red
$deleted = 0; $moved = 0; $failed = 0

foreach ($i in $plan) {
    try {
        switch ($i.Action) {
            'DELETE' {
                Remove-Item -LiteralPath $i.Path -Force -ErrorAction Stop
                Write-Host "  DELETED $($i.Path)" -ForegroundColor DarkRed
                $deleted++
            }
            'MOVE' {
                $destDir = Join-Path $modelsDir ($i.Detail -replace '^-> models/', '' -replace '/$', '')
                if (-not (Test-Path $destDir)) {
                    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                }
                $target = Join-Path $destDir (Split-Path -Leaf $i.Path)
                if (Test-Path $target) {
                    Write-Host "  SKIP (target exists) $target" -ForegroundColor Yellow
                    $failed++
                } else {
                    Move-Item -LiteralPath $i.Path -Destination $target -ErrorAction Stop
                    Write-Host "  MOVED $($i.Path) -> $target" -ForegroundColor DarkYellow
                    $moved++
                }
            }
            'REVIEW' { }
        }
    } catch {
        Write-Host "  FAIL $($i.Path): $($_.Exception.Message)" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "Done: $deleted deleted, $moved moved, $failed failed/skipped" -ForegroundColor Cyan
Write-Host "Re-run scripts/scan-inventory.ps1 to refresh state/inventory.json." -ForegroundColor Yellow
