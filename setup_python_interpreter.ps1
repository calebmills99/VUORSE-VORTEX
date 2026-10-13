$ErrorActionPreference = "Stop"

$projectRoot = (Get-Location).Path

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "python not found in PATH. Install Python 3.12+ and retry."
    exit 1
}

uv venv .venv --python (Get-Command python).Source

Write-Host "Virtual environment created at $projectRoot\.venv"

$settingsDir = Join-Path $projectRoot ".vscode"
New-Item -ItemType Directory -Force -Path $settingsDir | Out-Null

$settingsPath = Join-Path $settingsDir "settings.json"
$interpreterPath = "$projectRoot\.venv\Scripts\python.exe"

# ConvertTo-Json escapes the backslashes in a Windows path; a here-string
# would write them raw and leave settings.json unparseable.
[ordered]@{
    "python.defaultInterpreterPath" = $interpreterPath
    "python.venvPath"               = ".venv"
} | ConvertTo-Json | Set-Content -Path $settingsPath -Encoding utf8

Write-Host "settings written to $settingsPath"
Write-Host "Setup complete. Restart VS Code to pick up the new interpreter."
