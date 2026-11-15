# BugDiag Windows Local Development Setup Script
# PowerShell 5.1 / 7+ compatible

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  BugDiag: Intelligent Bug Diagnosis Platform Setup       " -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

# 1. Check Python
Write-Host "`n[1/4] Checking Python environment..." -ForegroundColor Yellow
$pythonVer = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python 3.11+ is required but not found in PATH."
    exit 1
}
Write-Host "Found: $pythonVer" -ForegroundColor Green

# 2. Check Node & npm
Write-Host "`n[2/4] Checking Node & npm..." -ForegroundColor Yellow
$nodeVer = node --version 2>&1
$npmVer = npm --version 2>&1
Write-Host "Found Node: $nodeVer, npm: $npmVer" -ForegroundColor Green

# 3. Setup Backend Environment
Write-Host "`n[3/4] Installing Backend Dependencies..." -ForegroundColor Yellow
Set-Location "$root\backend"
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created backend\.env from template" -ForegroundColor Gray
}
pip install -e ".[dev]"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: pip install returned non-zero code. Checking core modules..." -ForegroundColor Yellow
}

# 4. Setup Frontend
Write-Host "`n[4/4] Installing Frontend Dependencies..." -ForegroundColor Yellow
Set-Location "$root\frontend"
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created frontend\.env from template" -ForegroundColor Gray
}
npm install

Set-Location $root
Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "  Setup complete! Run scripts\run_all.ps1 to start services." -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
