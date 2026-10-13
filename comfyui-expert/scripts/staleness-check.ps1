# Staleness Check Hook (SessionStart)
# Reads references/staleness-report.md and reports what has actually aged out.
#
# Wired up by .claude/settings.json -> hooks.SessionStart.
# Safe to run by hand: pwsh -File scripts/staleness-check.ps1

$ErrorActionPreference = "Stop"

$repoRoot   = Split-Path -Parent $PSScriptRoot
$reportFile = Join-Path $repoRoot "references" "staleness-report.md"

# A hook must never break the session. Any failure degrades to a single line.
try {
    if (-not (Test-Path $reportFile)) {
        Write-Output "[VideoAgent] No staleness report at references/staleness-report.md. Run research to initialize."
        exit 0
    }

    $content = Get-Content -LiteralPath $reportFile -Raw -ErrorAction Stop

    if ($content -match "Not yet run") {
        Write-Output "[VideoAgent] Research has never been run. Consider asking: 'research latest ComfyUI updates'"
        exit 0
    }

    $now = Get-Date

    # --- Last full research run ------------------------------------------------
    if ($content -match '\*\*Date\*\*:\s*(\d{4}-\d{2}-\d{2})') {
        $lastRun = [datetime]::ParseExact($Matches[1], 'yyyy-MM-dd', $null)
        $daysSince = [int]($now - $lastRun).TotalDays

        if ($daysSince -gt 90) {
            Write-Output "[VideoAgent] Research data is $daysSince days old (last run $($Matches[1])). Model rankings are likely wrong. Ask: 'research latest ComfyUI updates'"
        } elseif ($daysSince -gt 14) {
            Write-Output "[VideoAgent] Research data is $daysSince days old. Consider asking: 'research latest ComfyUI updates'"
        }
    }

    # --- Per-file ages, computed from the date column --------------------------
    # The Status text in the report is prose and goes stale on its own, so the
    # dates are treated as the only authority here.
    $rows = [regex]::Matches($content, '(?m)^\|\s*`?([A-Za-z0-9._-]+\.md)`?\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|')

    $aged = @()
    foreach ($row in $rows) {
        $file = $row.Groups[1].Value
        try {
            $when = [datetime]::ParseExact($row.Groups[2].Value, 'yyyy-MM-dd', $null)
        } catch {
            continue
        }
        $age = [int]($now - $when).TotalDays
        # 90 days matches the "Models: 3 months" threshold in the report.
        if ($age -gt 90) {
            $aged += [pscustomobject]@{ File = $file; Days = $age }
        }
    }

    if ($aged.Count -gt 0) {
        $worst = $aged | Sort-Object Days -Descending | Select-Object -First 4
        $list = ($worst | ForEach-Object { "$($_.File) ($($_.Days)d)" }) -join ", "
        $extra = if ($aged.Count -gt 4) { " +$($aged.Count - 4) more" } else { "" }
        Write-Output "[VideoAgent] $($aged.Count) reference(s) past the 90-day threshold: $list$extra"
    }

    # --- Inventory freshness ---------------------------------------------------
    $inventoryFile = Join-Path $repoRoot "state" "inventory.json"
    if (-not (Test-Path $inventoryFile)) {
        Write-Output "[VideoAgent] No state/inventory.json. Workflow validation is disabled until you run: pwsh -File scripts/scan-inventory.ps1 -ComfyUIPath <path>"
    } else {
        $invAge = [int]($now - (Get-Item -LiteralPath $inventoryFile).LastWriteTime).TotalDays
        if ($invAge -gt 30) {
            Write-Output "[VideoAgent] state/inventory.json is $invAge days old. Re-scan if you have installed models since."
        }
    }
} catch {
    Write-Output "[VideoAgent] Staleness check failed: $($_.Exception.Message)"
}

exit 0
