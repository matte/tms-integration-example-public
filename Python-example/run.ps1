<#
    Windows launcher for the TMS Gateway console.

    Creates a virtual environment in .venv the first time, installs the
    dependencies, then starts the console. Any arguments are passed through:

        .\run.ps1
        .\run.ps1 --environment qa --username me@engagedtechnologies.com
        .\run.ps1 --browser-login

    If PowerShell refuses to run this file, allow it for this window only:

        Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#>
$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Host "Creating the virtual environment in .venv ..." -ForegroundColor Cyan
    & py -3 -m venv (Join-Path $root ".venv")
    if ($LASTEXITCODE -ne 0) { & python -m venv (Join-Path $root ".venv") }
}

Write-Host "Installing dependencies ..." -ForegroundColor Cyan
& $python -m pip install --quiet --upgrade pip
& $python -m pip install --quiet -r (Join-Path $root "requirements.txt")

& $python -m tms_cli @args
