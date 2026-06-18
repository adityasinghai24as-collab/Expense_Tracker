# start-dev.ps1
# Starts the full Expense Tracker stack: Database (Docker) + Backend (FastAPI) + Frontend (React/Vite)

Write-Host "Starting Expense Tracker Local Environment..." -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Get the root directory
$rootDir = Get-Location

# 1. Start the Database (Docker Compose - background)
Write-Host "`n[1/3] Spinning up PostgreSQL via Docker..." -ForegroundColor Cyan
docker compose up -d

Write-Host "     ✓ Database starting (waiting 3 seconds for initialization)..." -ForegroundColor DarkCyan
Start-Sleep -Seconds 3

# 2. Start the Backend (FastAPI - new window)
Write-Host "`n[2/3] Launching FastAPI Backend on port 8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit -Command `"cd $rootDir\backend; Write-Host 'Backend starting... Press Ctrl+C to stop' -ForegroundColor Yellow; python main.py`""

# 3. Start the Frontend (Vite - new window)
Write-Host "[3/3] Launching Vite React Frontend on port 5173..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit -Command `"cd $rootDir\frontend; Write-Host 'Frontend starting... Press Ctrl+C to stop' -ForegroundColor Yellow; npm run dev`""

Write-Host "`n===============================================" -ForegroundColor Green
Write-Host "✅ All services launched successfully!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host "`n📍 Services running at:" -ForegroundColor Green
Write-Host "   • Database:    PostgreSQL on localhost:5432" -ForegroundColor DarkCyan
Write-Host "   • Backend API: http://localhost:8000" -ForegroundColor DarkCyan
Write-Host "   • API Docs:    http://localhost:8000/docs" -ForegroundColor DarkCyan
Write-Host "   • Frontend:    http://localhost:5173" -ForegroundColor DarkCyan
Write-Host "`n💡 Tip: Use 'docker compose ps' to view container status" -ForegroundColor Gray
Write-Host "💡 Tip: Use 'docker compose logs -f backend' to view backend logs" -ForegroundColor Gray
Write-Host "`n"