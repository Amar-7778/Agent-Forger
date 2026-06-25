# run_prototype.ps1
# Helper script to run both FastAPI backend and Vite frontend for AgentForge prototype

$wsRoot = Get-Item -Path "."
$backendDir = Join-Path $wsRoot.FullName "Back-end"
$frontendDir = Join-Path $wsRoot.FullName "Front-end"

Write-Host "Starting AgentForge Prototype..." -ForegroundColor Cyan

# 1. Start FastAPI backend in a new console window
Write-Host "Launching FastAPI backend server..." -ForegroundColor Green
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; .\venv\Scripts\python.exe main.py" -WindowStyle Normal

# 2. Start Vite frontend in a new console window
Write-Host "Launching Vite/TanStack frontend..." -ForegroundColor Green
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", "cd '$frontendDir'; npm run dev" -WindowStyle Normal

Write-Host "Both servers launched!" -ForegroundColor Cyan
Write-Host "- FastAPI Backend: http://127.0.0.1:8000" -ForegroundColor Gray
Write-Host "- Vite Frontend: http://localhost:5173" -ForegroundColor Yellow
