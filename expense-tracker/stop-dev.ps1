# stop-dev.ps1

Write-Host "Shutting down Expense Tracker Local Environment..." -ForegroundColor Yellow

# Stop and remove the Docker container
docker compose down

Write-Host "Environment gracefully stopped." -ForegroundColor Green