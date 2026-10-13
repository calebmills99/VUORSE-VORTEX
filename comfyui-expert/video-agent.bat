-@echo off
REM ============================================================
REM  VideoAgent Launcher
REM  Opens Claude Code with the full VideoAgent context loaded.
REM
REM  Usage:
REM    video-agent.bat                     Start a session
REM    video-agent.bat --resume            Resume last session
REM    video-agent.bat --project MyVideo   Set active project
REM    video-agent.bat --comfyui URL       Override ComfyUI URL
REM ============================================================

setlocal enabledelayedexpansion

REM Resolve to the directory where this bat file lives (strips trailing backslash)
set "REPO_DIR=%~dp0"
if "%REPO_DIR:~-1%"=="\" set "REPO_DIR=%REPO_DIR:~0,-1%"
set "CLAUDE_ARGS="
set "ACTIVE_PROJECT="
set "COMFYUI_URL=http://127.0.0.1:8188"

REM Parse arguments
:parse_args
if "%~1"=="" goto :done_args
if /i "%~1"=="--resume" (
    set "CLAUDE_ARGS=--resume"
    shift
    goto :parse_args
)
if /i "%~1"=="--project" (
    set "ACTIVE_PROJECT=%~2"
    shift & shift
    goto :parse_args
)
if /i "%~1"=="--comfyui" (
    set "COMFYUI_URL=%~2"
    shift & shift
    goto :parse_args
)
shift
goto :parse_args
:done_args

REM Write active session config (read by CLAUDE.md).
REM Built with PowerShell so the timestamp is ISO-8601 and the JSON has no
REM trailing whitespace -- "echo >>" produced both, and a locale-formatted
REM %date% %time% that nothing could parse.
set "SESSION_FILE=%REPO_DIR%\state\session.json"
if not exist "%REPO_DIR%\state" mkdir "%REPO_DIR%\state"

pwsh -NoProfile -Command ^
  "$o=[ordered]@{comfyui_url='%COMFYUI_URL%';active_project='%ACTIVE_PROJECT%';started=(Get-Date).ToString('o')}; $o|ConvertTo-Json|Set-Content -LiteralPath '%SESSION_FILE%' -Encoding UTF8" 2>nul

if errorlevel 1 (
    echo  [warn] Could not write session.json via pwsh - falling back to plain echo.
    >  "%SESSION_FILE%" echo {
    >> "%SESSION_FILE%" echo   "comfyui_url": "%COMFYUI_URL%",
    >> "%SESSION_FILE%" echo   "active_project": "%ACTIVE_PROJECT%",
    >> "%SESSION_FILE%" echo   "started": ""
    >> "%SESSION_FILE%" echo }
)

REM Launch Claude Code in the VideoAgent directory
cd /d "%REPO_DIR%"
echo.
echo  VideoAgent Session
echo  ==================
echo  Project dir: %REPO_DIR%
if defined ACTIVE_PROJECT echo  Project:     %ACTIVE_PROJECT%
echo  ComfyUI:     %COMFYUI_URL%
echo.

claude %CLAUDE_ARGS%

endlocal
rewrite this for codex. a **Codex-native version** with better argument handling,

Here’s a **Codex-native rewrite** of your batch launcher with **cleaner argument handling**, proper `--key=value` support, validation, help text, and a session file written for Codex instead of Claude.

I’m giving you a **Windows batch version** first, since your original is `.bat`.

---

## `video-agent-codex.bat`

```bat
@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================
REM  VideoAgent Launcher for Codex
REM  Opens Codex with the full VideoAgent context loaded.
REM
REM  Usage:
REM    video-agent-codex.bat
REM    video-agent-codex.bat --resume
REM    video-agent-codex.bat --project MyVideo
REM    video-agent-codex.bat --project="My Video"
REM    video-agent-codex.bat --comfyui http://127.0.0.1:8188
REM    video-agent-codex.bat --comfyui=http://127.0.0.1:8188
REM    video-agent-codex.bat --resume --project MyVideo
REM
REM  Supported args:
REM    --resume
REM    --project <name>
REM    --project=<name>
REM    --comfyui <url>
REM    --comfyui=<url>
REM    --help | -h | /?
REM ============================================================

REM Resolve repo dir from script location, strip trailing slash
set "REPO_DIR=%~dp0"
if "%REPO_DIR:~-1%"=="\" set "REPO_DIR=%REPO_DIR:~0,-1%"

REM Defaults
set "CODEX_ARGS="
set "RESUME=0"
set "ACTIVE_PROJECT="
set "COMFYUI_URL=http://127.0.0.1:8188"
set "SESSION_DIR=%REPO_DIR%\state"
set "SESSION_FILE=%SESSION_DIR%\session.json"

REM ------------------------------------------------------------
REM Parse arguments
REM ------------------------------------------------------------
:parse_args
if "%~1"=="" goto :done_args

set "ARG=%~1"

if /I "%ARG%"=="--help"  goto :usage
if /I "%ARG%"=="-h"      goto :usage
if /I "%ARG%"=="/?"      goto :usage

if /I "%ARG%"=="--resume" (
    set "RESUME=1"
    shift
    goto :parse_args
)

if /I "%ARG%"=="--project" (
    if "%~2"=="" (
        echo [error] Missing value for --project
        goto :usage_error
    )
    set "ACTIVE_PROJECT=%~2"
    shift
    shift
    goto :parse_args
)

if /I "%ARG%"=="--comfyui" (
    if "%~2"=="" (
        echo [error] Missing value for --comfyui
        goto :usage_error
    )
    set "COMFYUI_URL=%~2"
    shift
    shift
    goto :parse_args
)

REM Support --project=value
echo "%ARG%" | findstr /B /I /C:"--project=" >nul
if not errorlevel 1 (
    set "ACTIVE_PROJECT=%ARG:~10%"
    shift
    goto :parse_args
)

REM Support --comfyui=value
echo "%ARG%" | findstr /B /I /C:"--comfyui=" >nul
if not errorlevel 1 (
    set "COMFYUI_URL=%ARG:~10%"
    shift
    goto :parse_args
)

echo [error] Unknown argument: %ARG%
goto :usage_error

:done_args

REM ------------------------------------------------------------
REM Build Codex args
REM ------------------------------------------------------------
if "%RESUME%"=="1" set "CODEX_ARGS=%CODEX_ARGS% --resume"

REM ------------------------------------------------------------
REM Ensure state directory exists
REM ------------------------------------------------------------
if not exist "%SESSION_DIR%" mkdir "%SESSION_DIR%"

REM ------------------------------------------------------------
REM Write session config
REM Prefer PowerShell for valid JSON + ISO-8601 timestamp
REM ------------------------------------------------------------
where pwsh >nul 2>nul
if not errorlevel 1 goto :write_with_pwsh

where powershell >nul 2>nul
if not errorlevel 1 goto :write_with_windows_powershell

goto :write_fallback

:write_with_pwsh
pwsh -NoProfile -Command ^
  "$o=[ordered]@{tool='codex';comfyui_url='%COMFYUI_URL%';active_project='%ACTIVE_PROJECT%';resume=%RESUME%;started=(Get-Date).ToString('o')}; $o | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath '%SESSION_FILE%' -Encoding UTF8" 2>nul
if errorlevel 1 goto :write_fallback
goto :launch

:write_with_windows_powershell
powershell -NoProfile -Command ^
  "$o=[ordered]@{tool='codex';comfyui_url='%COMFYUI_URL%';active_project='%ACTIVE_PROJECT%';resume=%RESUME%;started=(Get-Date).ToString('o')}; $o | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath '%SESSION_FILE%' -Encoding UTF8" 2>nul
if errorlevel 1 goto :write_fallback
goto :launch

:write_fallback
echo [warn] Could not write session.json via PowerShell. Falling back to plain JSON.
> "%SESSION_FILE%" echo {
>>"%SESSION_FILE%" echo   "tool": "codex",
>>"%SESSION_FILE%" echo   "comfyui_url": "%COMFYUI_URL%",
>>"%SESSION_FILE%" echo   "active_project": "%ACTIVE_PROJECT%",
>>"%SESSION_FILE%" echo   "resume": %RESUME%,
>>"%SESSION_FILE%" echo   "started": ""
>>"%SESSION_FILE%" echo }

REM ------------------------------------------------------------
REM Launch Codex
REM ------------------------------------------------------------
:launch
cd /d "%REPO_DIR%" || (
    echo [error] Could not change directory to: %REPO_DIR%
    exit /b 1
)

echo.
echo  VideoAgent Session
echo  ==================
echo  Tool:        Codex
echo  Project dir: %REPO_DIR%
if defined ACTIVE_PROJECT echo  Project:     %ACTIVE_PROJECT%
echo  ComfyUI:     %COMFYUI_URL%
if "%RESUME%"=="1" echo  Resume:      yes
echo.

where codex >nul 2>nul
if errorlevel 1 (
    echo [error] 'codex' was not found on PATH.
    echo         Install it or update this script to point to the executable.
    exit /b 1
)

codex %CODEX_ARGS%
set "EXIT_CODE=%ERRORLEVEL%"

endlocal & exit /b %EXIT_CODE%

:usage
echo.
echo Usage:
echo   video-agent-codex.bat [options]
echo.
echo Options:
echo   --resume                 Resume last Codex session
echo   --project NAME           Set active project
echo   --project=NAME           Set active project
echo   --comfyui URL            Override ComfyUI URL
echo   --comfyui=URL            Override ComfyUI URL
echo   --help, -h, /?           Show this help
echo.
exit /b 0

:usage_error
echo.
echo Run with --help for usage.
exit /b 1
