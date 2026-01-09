# Fetch and checkout to main branch
Write-Host "Fetching and checking out main branch..." -ForegroundColor Cyan
git fetch origin
git checkout main
git pull origin main

# Open the application link in the default browser
# We do this slightly before or as the app starts
Write-Host "Opening browser at http://127.0.0.1:8050 ..." -ForegroundColor Cyan
Start-Process "http://127.0.0.1:8050"

# Run the application using uv
Write-Host "Running application uv run app.py..." -ForegroundColor Green
uv run app.py
