# Quick script to run Law-GPT in development mode
# This script starts both backend and frontend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "      Law-GPT Development Server       " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    .\.venv\Scripts\Activate.ps1
    pip install -r backend\requirements.txt
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Check if node_modules exists
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

Write-Host ""
Write-Host "🚀 Starting services..." -ForegroundColor Green
Write-Host ""

# Start backend in new window
Write-Host "  ✓ Backend will start on http://localhost:8000" -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host '🔥 Backend Server' -ForegroundColor Cyan; Write-Host ''; & '.\.venv\Scripts\Activate.ps1'; cd backend; uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend in new window
Write-Host "  ✓ Frontend will start on http://localhost:5173" -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host '⚡ Frontend Server' -ForegroundColor Cyan; Write-Host ''; cd frontend; npm run dev"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ Development servers starting...    " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access your application at:" -ForegroundColor Yellow
Write-Host "  Frontend: " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:5173" -ForegroundColor Cyan
Write-Host "  Backend:  " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs: " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop the servers" -ForegroundColor Gray
Write-Host ""
