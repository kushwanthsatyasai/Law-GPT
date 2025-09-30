# PowerShell script to migrate SQLite data to PostgreSQL
# Usage: .\scripts\migrate_to_postgres.ps1

param(
    [string]$PostgresUrl = $env:DATABASE_URL
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SQLite to PostgreSQL Migration Tool  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "❌ Virtual environment not found. Please run: python -m venv .venv" -ForegroundColor Red
    exit 1
}

# Check if PostgreSQL URL is provided
if (-not $PostgresUrl) {
    Write-Host "❌ PostgreSQL URL not provided!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please provide PostgreSQL connection URL:" -ForegroundColor Yellow
    Write-Host "  Option 1: Set DATABASE_URL environment variable" -ForegroundColor Gray
    Write-Host "  Option 2: Pass as parameter: .\scripts\migrate_to_postgres.ps1 'postgresql://user:pass@host:5432/dbname'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Example:" -ForegroundColor Yellow
    Write-Host "  `$env:DATABASE_URL='postgresql://lawgpt:password@localhost:5432/lawgpt'" -ForegroundColor Gray
    Write-Host "  .\scripts\migrate_to_postgres.ps1" -ForegroundColor Gray
    exit 1
}

# Check if SQLite database exists
if (-not (Test-Path "data\lawgpt.db")) {
    Write-Host "❌ SQLite database not found at data\lawgpt.db" -ForegroundColor Red
    exit 1
}

Write-Host "📦 Installing required packages..." -ForegroundColor Yellow
pip install psycopg[binary] -q

Write-Host ""
Write-Host "🚀 Starting migration..." -ForegroundColor Green
Write-Host ""

# Run the migration script
python scripts\migrate_sqlite_to_postgres.py $PostgresUrl

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✅ Migration Completed Successfully!  " -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Update your .env file with the PostgreSQL DATABASE_URL" -ForegroundColor Gray
    Write-Host "  2. Test the backend: uvicorn backend.app.main:app --reload" -ForegroundColor Gray
    Write-Host "  3. Deploy to production!" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "❌ Migration failed. Please check the error messages above." -ForegroundColor Red
    exit 1
}
