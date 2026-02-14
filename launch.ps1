# launch.ps1 — Start both servers for local development

$backendPort = 8000
$frontendPort = 5173
$frontendUrl = "http://localhost:$frontendPort/products/pressurize/"

Write-Host "Starting Pressurize..." -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
	"cd '$scriptDir\backend'; uv run python -m pressurize" `
	-WindowStyle Normal

# Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
	"cd '$scriptDir\frontend'; npm.cmd run dev" `
	-WindowStyle Normal

Start-Sleep -Seconds 3
Start-Process $frontendUrl
Write-Host "Launched: $frontendUrl" -ForegroundColor Green
