# BugDiag Multi-Process Launcher for Windows PowerShell
# Starts both Backend and Frontend in separate concurrent terminal windows or background jobs

Write-Host "Starting BugDiag Services..." -ForegroundColor Cyan

$root = Split-Path -Parent $PSScriptRoot

# Start Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\backend'; uvicorn bugdiag.main:app --reload --host 127.0.0.1 --port 8000"
Write-Host "Backend API launched at http://localhost:8000 (Swagger docs at http://localhost:8000/docs)" -ForegroundColor Green

# Start Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm run dev"
Write-Host "Frontend launched at http://localhost:5173" -ForegroundColor Green

Write-Host "`nBugDiag platform initialized successfully!" -ForegroundColor Cyan
