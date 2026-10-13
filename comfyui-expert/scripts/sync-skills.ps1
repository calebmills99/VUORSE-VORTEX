<#
.SYNOPSIS
    Mirrors canonical references into skill folders, then optionally publishes the
    Claude compatibility copies to ~/.claude/skills/.
.DESCRIPTION
    Two stages, run in this order:

      1. MIRROR  references/*.md  ->  skills/comfyui-character-gen/references/
         The repo-root references/ directory is canonical. The skill keeps its own
         copy because it is synced to ~/.claude/skills where it cannot reach the
         repo root. Mirroring first is what stops the two from drifting.

      2. CLAUDE ADAPTER  skills/<name>/  ->  ~/.claude/skills/<name>/
         SKILL.md plus references/ and eval/ if present.

    This script replaces the old deploy.ps1, which wrote to the same destination
    from a different source and silently fought with this one.
.EXAMPLE
    pwsh -File scripts/sync-skills.ps1
    pwsh -File scripts/sync-skills.ps1 -DryRun
    pwsh -File scripts/sync-skills.ps1 -Skill comfyui-character-gen
    pwsh -File scripts/sync-skills.ps1 -MirrorOnly
#>
param(
    [switch]$DryRun,
    [switch]$MirrorOnly,
    [string]$Skill
)

$ErrorActionPreference = "Stop"

$RepoRoot   = Split-Path -Parent $PSScriptRoot
$LocalBase  = Join-Path $RepoRoot "skills"
$CanonRefs  = Join-Path $RepoRoot "references"
$GlobalBase = Join-Path $env:USERPROFILE ".claude" "skills"

# Skills published through the Claude compatibility adapter. Add new ones here.
$GlobalSkills = @(
    "comfyui-character-gen",
    "comfyui-prompt-interview",
    "comfyui-video-production",
    "comfyui-workflow-builder"
)

# Which canonical reference files each skill carries a copy of.
# Anything not listed stays skill-local (e.g. talking-head-workflows.md).
$MirrorMap = @{
    "comfyui-character-gen" = @(
        "models.md",
        "workflows.md",
        "lora-training.md",
        "voice-synthesis.md",
        "evolution.md"
    )
    "comfyui-video-production" = @(
        "workflows.md",
        "troubleshooting.md"
    )
    "comfyui-workflow-builder" = @(
        "models.md",
        "workflows.md",
        "prompt-templates.md"
    )
}

Write-Host "VideoAgent Skill Sync" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host "Repo:   $RepoRoot"
Write-Host "Global: $GlobalBase"
if ($DryRun) { Write-Host "Mode:   DRY RUN (nothing will be written)" -ForegroundColor Yellow }
Write-Host ""

if ($Skill) {
    if ($Skill -notin $GlobalSkills) {
        Write-Host "Warning: '$Skill' is not in the global skills list. Syncing anyway." -ForegroundColor Yellow
    }
    $GlobalSkills = @($Skill)
}

# ---- Stage 1: mirror canonical references into skill folders -----------------

Write-Host "[1/2] Mirroring canonical references" -ForegroundColor Yellow

$mirrored = 0
$mirrorSkipped = 0

foreach ($skillName in $GlobalSkills) {
    if (-not $MirrorMap.ContainsKey($skillName)) { continue }

    $destRefs = Join-Path $LocalBase $skillName "references"
    if (-not (Test-Path $destRefs)) {
        if ($DryRun) {
            Write-Host "  WOULD CREATE $destRefs" -ForegroundColor Cyan
        } else {
            New-Item -ItemType Directory -Path $destRefs -Force | Out-Null
        }
    }

    foreach ($ref in $MirrorMap[$skillName]) {
        $src = Join-Path $CanonRefs $ref
        $dst = Join-Path $destRefs $ref

        if (-not (Test-Path $src)) {
            Write-Host "  MISSING: references/$ref (canonical source absent)" -ForegroundColor Red
            $mirrorSkipped++
            continue
        }

        $srcHash = (Get-FileHash -LiteralPath $src).Hash
        $dstHash = if (Test-Path $dst) { (Get-FileHash -LiteralPath $dst).Hash } else { "" }

        if ($srcHash -eq $dstHash) {
            $mirrorSkipped++
            continue
        }

        if ($DryRun) {
            Write-Host "  WOULD MIRROR $ref -> $skillName/references/" -ForegroundColor Cyan
        } else {
            try {
                Copy-Item -LiteralPath $src -Destination $dst -Force
                Write-Host "  MIRRORED $ref -> $skillName/references/" -ForegroundColor Green
            } catch {
                Write-Host "  FAIL: could not mirror ${ref}: $($_.Exception.Message)" -ForegroundColor Red
                $mirrorSkipped++
                continue
            }
        }
        $mirrored++
    }
}

Write-Host "  Mirrored: $mirrored, already in sync: $mirrorSkipped"
Write-Host ""

if ($MirrorOnly) {
    Write-Host "MirrorOnly set -- stopping before global publish." -ForegroundColor Yellow
    exit 0
}

# ---- Stage 2: publish skills to global --------------------------------------

Write-Host "[2/2] Publishing Claude compatibility skills" -ForegroundColor Yellow

$synced = 0
$skipped = 0

foreach ($skillName in $GlobalSkills) {
    $localPath = Join-Path $LocalBase $skillName
    $globalPath = Join-Path $GlobalBase $skillName
    $localSkillMd = Join-Path $localPath "SKILL.md"

    if (-not (Test-Path $localSkillMd)) {
        Write-Host "  SKIP: $skillName (no local SKILL.md)" -ForegroundColor Yellow
        $skipped++
        continue
    }

    # Compare the whole payload, not just SKILL.md -- a references-only change
    # used to be silently skipped by the old hash check.
    $localFiles = Get-ChildItem -LiteralPath $localPath -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch '\\eval\\results\\' }
    $localSig = ($localFiles | Sort-Object FullName | ForEach-Object {
        "$($_.FullName.Substring($localPath.Length)):$((Get-FileHash -LiteralPath $_.FullName).Hash)"
    }) -join "|"

    $globalSig = ""
    if (Test-Path $globalPath) {
        $globalFiles = Get-ChildItem -LiteralPath $globalPath -File -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -notmatch '\\eval\\results\\' }
        $globalSig = ($globalFiles | Sort-Object FullName | ForEach-Object {
            "$($_.FullName.Substring($globalPath.Length)):$((Get-FileHash -LiteralPath $_.FullName).Hash)"
        }) -join "|"
    }

    if ($localSig -eq $globalSig) {
        Write-Host "  OK: $skillName (already in sync)" -ForegroundColor Green
        $skipped++
        continue
    }

    if ($DryRun) {
        Write-Host "  WOULD SYNC: $skillName" -ForegroundColor Cyan
        $synced++
        continue
    }

    try {
        if (-not (Test-Path $globalPath)) {
            New-Item -ItemType Directory -Path $globalPath -Force | Out-Null
        }

        Copy-Item -LiteralPath $localSkillMd -Destination (Join-Path $globalPath "SKILL.md") -Force
        Write-Host "  SYNCED: $skillName/SKILL.md" -ForegroundColor Green

        foreach ($sub in @("references", "eval")) {
            $localSub = Join-Path $localPath $sub
            if (-not (Test-Path $localSub)) { continue }
            if (-not (Get-ChildItem -LiteralPath $localSub -Recurse -File -ErrorAction SilentlyContinue)) { continue }

            $globalSub = Join-Path $globalPath $sub
            if (-not (Test-Path $globalSub)) {
                New-Item -ItemType Directory -Path $globalSub -Force | Out-Null
            }
            Copy-Item -Path (Join-Path $localSub "*") -Destination $globalSub -Recurse -Force
            Write-Host "    + $sub/" -ForegroundColor DarkGreen
        }
    } catch {
        Write-Host "  FAIL: $skillName -- $($_.Exception.Message)" -ForegroundColor Red
        $skipped++
        continue
    }

    $synced++
}

Write-Host ""
Write-Host "Done: $synced synced, $skipped skipped" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "(Dry run - no files were changed)" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "NOTE: Only the listed skills are copied into the Claude compatibility layer." -ForegroundColor Yellow
Write-Host "      Canonical repository skills remain session-scoped under skills/." -ForegroundColor Yellow
