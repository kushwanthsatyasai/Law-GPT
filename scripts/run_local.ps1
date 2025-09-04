# Run Law-GPT locally

# Activate virtual environment if it exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..."
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "Virtual environment not found. Please create it first."
    Write-Host "Run: python -m venv .venv"
    exit 1
}

# Setup SQLite if PostgreSQL is not available
$pgInstalled = Get-Command psql -ErrorAction SilentlyContinue
if (-not $pgInstalled) {
    Write-Host "PostgreSQL is not installed. Using SQLite instead..."
    & "$PSScriptRoot\setup_sqlite.ps1"
}

# Start backend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ./backend; uvicorn app.main:app --reload --port 8000"

# Start frontend in this window
Write-Host "Starting frontend..."
Set-Location -Path "./frontend"
npm run dev