$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root 'backend'
$Frontend = Join-Path $Root 'frontend'

Write-Host 'TraceIQ Milestone 1 verification' -ForegroundColor Cyan

Write-Host "`n[1/3] Python syntax compilation" -ForegroundColor Yellow
Push-Location $Backend
try {
    python -m compileall -q bugdiag tests
    if ($LASTEXITCODE -ne 0) { throw 'Python compilation failed.' }

    Write-Host "`n[2/3] Backend test suite" -ForegroundColor Yellow
    python -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' }
}
finally {
    Pop-Location
}

Write-Host "`n[3/3] Frontend clean install and production build" -ForegroundColor Yellow
Push-Location $Frontend
try {
    npm ci
    if ($LASTEXITCODE -ne 0) { throw 'npm ci failed.' }
    npm run build
    if ($LASTEXITCODE -ne 0) { throw 'Frontend production build failed.' }
}
finally {
    Pop-Location
}

Write-Host "`nMilestone 1 verification commands completed successfully." -ForegroundColor Green
