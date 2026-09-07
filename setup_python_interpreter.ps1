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

$settings = [ordered]@{
    "python.defaultInterpreterPath" = $interpreterPath
    "python.venvPath"               = ".venv"
}
$settings | ConvertTo-Json -Depth 2 | Set-Content -Path $settingsPath -Encoding utf8

Write-Host "VS Code settings written to $settingsPath"
Write-Host "Setup complete. Restart VS Code to pick up the new interpreter."
