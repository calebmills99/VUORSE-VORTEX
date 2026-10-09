<#
.SYNOPSIS
    Convene a Galactic Summit. Poll the AI council on a docket of motions and
    produce a ballot for the Steward Vessel to rule on.

.DESCRIPTION
    The council ADVISES. The Steward RULES.

    This script calls three council members — Mistral (HTTP), OpenAI Codex CLI,
    and GitHub Copilot CLI — with each motion in turn, records what each one
    says, and writes a ballot. It ratifies nothing. It promotes nothing. It
    cannot write to canon/ and refuses to try.

    Output lands in the run directory beside the motions file, which is under
    worldforge/ and therefore provisional by doctrine.

.PARAMETER MotionsPath
    JSON docket. Default: worldforge/2026-09-05-seventh-summit/motions.json

.PARAMETER Council
    Which members to poll. Default: all three. Absent members are recorded as
    abstaining, not as failures.

.PARAMETER DryRun
    Print the prompt each member would receive and exit. No network, no spend.

.EXAMPLE
    .\scripts\Convene-Summit.ps1 -DryRun
    .\scripts\Convene-Summit.ps1
    .\scripts\Convene-Summit.ps1 -Council mistral,copilot
#>
[CmdletBinding()]
param(
    [string]   $MotionsPath = "worldforge/2026-09-05-seventh-summit/motions.json",
    [string[]] $Council     = @("mistral", "codex", "copilot"),
    [string]   $MistralModel = "mistral-large-latest",
    [int]      $TimeoutSec  = 90,
    [switch]   $DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Snap     = "Snap. Snap. Snap."

# --------------------------------------------------------------------------
# guardrails
# --------------------------------------------------------------------------

function Assert-NotCanon {
    param([string] $Path)
    $full = [IO.Path]::GetFullPath((Join-Path $RepoRoot $Path))
    $canon = [IO.Path]::GetFullPath((Join-Path $RepoRoot "canon"))
    if ($full.StartsWith($canon, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to write inside canon/: $Path`n" +
              "  why : the council advises, it does not promote`n" +
              "  next: this script writes only under the run directory"
    }
}

# --------------------------------------------------------------------------
# the charge put to every council member
# --------------------------------------------------------------------------

function New-Charge {
    param([object] $Docket, [object] $Motion)
    @"
$Snap

You are seated at the $($Docket.summit) of the Golden Wingers Intergalactic League,
convened $($Docket.convened). The Three Snap Protocol has opened the proceeding.

$($Docket.preamble)

MOTION $($Motion.id) — $($Motion.title)

FINDING
$($Motion.finding)

QUESTION
$($Motion.question)

Answer in exactly this shape, nothing before or after:

VERDICT: <one of RATIFY / RATIFY WITH AMENDMENT / REJECT / ABSTAIN>
REASONING: <at most four sentences, concrete>
AMENDMENT: <the exact rule text you would enter, or NONE>
RISK: <what this ruling costs if it is wrong, or NONE>

You are advising a human steward who holds sole authority to promote canon.
Do not assume the ruling. Do not soften a real objection.
"@
}

# --------------------------------------------------------------------------
# council members — each returns a transcript string or throws
# --------------------------------------------------------------------------

function Invoke-Mistral {
    param([string] $Charge)

    $key = $env:MISTRAL_API_KEY
    if ([string]::IsNullOrWhiteSpace($key)) { $key = $env:MISTRAL_KEY }
    if ([string]::IsNullOrWhiteSpace($key)) {
        throw "MISTRAL_API_KEY is not set in this shell. Set it, or drop mistral from -Council."
    }

    $body = @{
        model    = $MistralModel
        messages = @(@{ role = "user"; content = $Charge })
        temperature = 0.3
    } | ConvertTo-Json -Depth 6 -Compress

    $args = @{
        Uri         = "https://api.mistral.ai/v1/chat/completions"
        Method      = "POST"
        Headers     = @{ Authorization = "Bearer $key"; "Content-Type" = "application/json" }
        Body        = [Text.Encoding]::UTF8.GetBytes($body)
        TimeoutSec  = $TimeoutSec
    }

    try {
        $res = Invoke-RestMethod @args
    } catch {
        throw "Mistral call failed: $($_.Exception.Message)`n" +
              "  model: $MistralModel`n" +
              "  next : 401 means the key is rejected, 429 means rate limited, " +
              "404 means the model name is wrong (try mistral-small-latest)."
    }
    return $res.choices[0].message.content
}

function Invoke-Codex {
    param([string] $Charge)

    $exe = Get-Command codex -ErrorAction SilentlyContinue
    if (-not $exe) {
        throw "codex CLI not found on PATH. Install the OpenAI Codex CLI, or drop codex from -Council."
    }

    $tmp = New-TemporaryFile
    try {
        Set-Content -Path $tmp -Value $Charge -Encoding utf8
        $out = & codex exec --skip-git-repo-check (Get-Content -Raw $tmp) 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0) {
            throw "codex exec returned exit $LASTEXITCODE`n$out"
        }
        return $out.Trim()
    } finally {
        Remove-Item $tmp -ErrorAction SilentlyContinue
    }
}

function Invoke-Copilot {
    param([string] $Charge)

    $exe = Get-Command copilot -ErrorAction SilentlyContinue
    if (-not $exe) {
        throw "copilot CLI not found on PATH. Install the GitHub Copilot CLI, or drop copilot from -Council."
    }

    $out = & copilot -p $Charge --allow-all-tools 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        throw "copilot returned exit $LASTEXITCODE`n$out"
    }
    return $out.Trim()
}

# --------------------------------------------------------------------------
# proceeding
# --------------------------------------------------------------------------

$docketFull = Join-Path $RepoRoot $MotionsPath
if (-not (Test-Path $docketFull)) {
    throw "No docket at $MotionsPath`n" +
          "  why : the Summit has no motions to put to the council`n" +
          "  next: pass -MotionsPath, or create the docket JSON first"
}

$docket  = Get-Content -Raw $docketFull | ConvertFrom-Json
$runDir  = Split-Path -Parent $MotionsPath
Assert-NotCanon $runDir

Write-Host ""
Write-Host $Snap -ForegroundColor Magenta
Write-Host "$($docket.summit) — $($docket.motions.Count) motions — council: $($Council -join ', ')" -ForegroundColor Magenta
Write-Host ""

if ($DryRun) {
    $m = $docket.motions[0]
    Write-Host "DRY RUN — charge for motion $($m.id), as each member would receive it:`n" -ForegroundColor Yellow
    Write-Host (New-Charge -Docket $docket -Motion $m)
    Write-Host "`nNo calls made. No spend. Re-run without -DryRun to convene." -ForegroundColor Yellow
    return
}

$ballot = [Collections.Generic.List[object]]::new()

foreach ($motion in $docket.motions) {
    Write-Host "MOTION $($motion.id) — $($motion.title)" -ForegroundColor Cyan
    $charge = New-Charge -Docket $docket -Motion $motion

    foreach ($member in $Council) {
        $seat = $member.ToLower()
        Write-Host ("  {0,-8} " -f $seat) -NoNewline

        try {
            $reply = switch ($seat) {
                "mistral" { Invoke-Mistral -Charge $charge }
                "codex"   { Invoke-Codex   -Charge $charge }
                "copilot" { Invoke-Copilot -Charge $charge }
                default   { throw "Unknown council member '$seat'. Known: mistral, codex, copilot." }
            }
            $verdict = if ($reply -match '(?im)^\s*VERDICT:\s*(.+)$') { $Matches[1].Trim() } else { "UNPARSED" }
            Write-Host $verdict -ForegroundColor Green
            $ballot.Add([pscustomobject]@{
                motion = $motion.id; title = $motion.title
                seat = $seat; verdict = $verdict; transcript = $reply; error = $null
            })
        } catch {
            Write-Host "ABSTAIN (unreachable)" -ForegroundColor DarkYellow
            Write-Host "           $($_.Exception.Message.Split("`n")[0])" -ForegroundColor DarkGray
            $ballot.Add([pscustomobject]@{
                motion = $motion.id; title = $motion.title
                seat = $seat; verdict = "ABSTAIN"; transcript = $null
                error = $_.Exception.Message
            })
        }
    }
    Write-Host ""
}

# --------------------------------------------------------------------------
# the ballot — advisory, unsigned
# --------------------------------------------------------------------------

$stamp      = Get-Date -Format "yyyy-MM-dd HH:mm"
$ballotPath = Join-Path $RepoRoot (Join-Path $runDir "ballot.md")
$jsonPath   = Join-Path $RepoRoot (Join-Path $runDir "council-transcripts.json")

$sb = [Text.StringBuilder]::new()
[void]$sb.AppendLine("# $($docket.summit) — Council Ballot")
[void]$sb.AppendLine()
[void]$sb.AppendLine("*$Snap*")
[void]$sb.AppendLine()
[void]$sb.AppendLine("Convened $($docket.convened) · polled $stamp · seats: $($Council -join ', ')")
[void]$sb.AppendLine()
[void]$sb.AppendLine("**The council advises. The Steward rules. Nothing below is canon.**")
[void]$sb.AppendLine()

foreach ($motion in $docket.motions) {
    [void]$sb.AppendLine("---")
    [void]$sb.AppendLine()
    [void]$sb.AppendLine("## Motion $($motion.id) — $($motion.title)")
    [void]$sb.AppendLine()
    [void]$sb.AppendLine("**Question**: $($motion.question)")
    [void]$sb.AppendLine()
    [void]$sb.AppendLine("| Seat | Verdict |")
    [void]$sb.AppendLine("|---|---|")
    foreach ($row in $ballot | Where-Object { $_.motion -eq $motion.id }) {
        [void]$sb.AppendLine("| $($row.seat) | $($row.verdict) |")
    }
    [void]$sb.AppendLine()
    foreach ($row in $ballot | Where-Object { $_.motion -eq $motion.id -and $_.transcript }) {
        [void]$sb.AppendLine("<details><summary>$($row.seat)</summary>")
        [void]$sb.AppendLine()
        [void]$sb.AppendLine('```')
        [void]$sb.AppendLine($row.transcript)
        [void]$sb.AppendLine('```')
        [void]$sb.AppendLine()
        [void]$sb.AppendLine("</details>")
        [void]$sb.AppendLine()
    }
    [void]$sb.AppendLine("### Steward's ruling")
    [void]$sb.AppendLine()
    [void]$sb.AppendLine("- [ ] RATIFY   - [ ] AMEND   - [ ] REJECT   - [ ] HOLD")
    [void]$sb.AppendLine()
    [void]$sb.AppendLine("> _ruling:_")
    [void]$sb.AppendLine()
}

[void]$sb.AppendLine("---")
[void]$sb.AppendLine()
[void]$sb.AppendLine("Signed, Steward Vessel: ______________________  Date: __________")
[void]$sb.AppendLine()
[void]$sb.AppendLine("No motion takes effect until this line is signed and the ruling is executed by hand.")

Set-Content -Path $ballotPath -Value $sb.ToString() -Encoding utf8
$ballot | ConvertTo-Json -Depth 8 | Set-Content -Path $jsonPath -Encoding utf8

Write-Host "ballot     -> $ballotPath" -ForegroundColor Green
Write-Host "transcripts-> $jsonPath"   -ForegroundColor Green
Write-Host ""
Write-Host "The council has advised. The floor is yours." -ForegroundColor Magenta
