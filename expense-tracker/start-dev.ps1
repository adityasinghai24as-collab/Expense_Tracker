# start-dev.ps1
# Starts the full Expense Tracker stack: Database (Docker) + Backend (FastAPI) + Frontend (React/Vite)

Write-Host "Starting Expense Tracker Local Environment..." -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Get the root directory (quoted to handle spaces in path)
$rootDir = (Get-Location).Path

# 1. Start the Database (Docker Compose - background)
# Only spin up the 'db' service. The backend runs natively (below) for easier debugging
# and hot-reload. The full 'docker compose up -d' is reserved for Phase 5 (containerized stack).
Write-Host "`n[1/3] Spinning up PostgreSQL via Docker..." -ForegroundColor Cyan
docker compose up db -d

Write-Host "     Database starting - waiting 3 seconds for initialization..." -ForegroundColor DarkCyan
Start-Sleep -Seconds 3

# 2. Start the Backend (FastAPI - new window)
Write-Host "`n[2/3] Launching FastAPI Backend on port 8000..." -ForegroundColor Cyan
$backendDir = Join-Path $rootDir "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$backendDir'; Write-Host 'Backend starting... Press Ctrl+C to stop' -ForegroundColor Yellow; python main.py"

# 3. Start the Frontend (Vite - new window)
Write-Host "[3/3] Launching Vite React Frontend on port 5173..." -ForegroundColor Cyan
$frontendDir = Join-Path $rootDir "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$frontendDir'; Write-Host 'Frontend starting... Press Ctrl+C to stop' -ForegroundColor Yellow; npm run dev"

Write-Host "`n===============================================" -ForegroundColor Green
Write-Host "All services launched successfully!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host "`nServices running at:" -ForegroundColor Green
Write-Host "   Database:    PostgreSQL on localhost:5432" -ForegroundColor DarkCyan
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor DarkCyan
Write-Host "   API Docs:    http://localhost:8000/docs" -ForegroundColor DarkCyan
Write-Host "   Frontend:    http://localhost:5173" -ForegroundColor DarkCyan
Write-Host "`nTip: Use 'docker compose ps' to view container status" -ForegroundColor Gray
Write-Host "Tip: Use 'docker compose logs -f db' to view database logs" -ForegroundColor Gray
Write-Host ""