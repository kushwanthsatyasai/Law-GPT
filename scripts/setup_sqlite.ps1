# SQLite setup script for Law-GPT local development

# Activate virtual environment if it exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..."
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "Virtual environment not found. Please create it first."
    Write-Host "Run: python -m venv .venv"
    exit 1
}

# Create SQLite database directory
$dbDir = "./data"
if (-not (Test-Path $dbDir)) {
    Write-Host "Creating database directory..."
    New-Item -ItemType Directory -Path $dbDir -Force | Out-Null
}

Write-Host "Setting up SQLite database for local development..."

# Update the .env file to use SQLite
$envPath = "./backend/.env"
$envContent = Get-Content $envPath -Raw

# Replace PostgreSQL settings with SQLite settings
$envContent = $envContent -replace "POSTGRES_HOST=.*", "DATABASE_URL=sqlite:///./data/lawgpt.db"

Set-Content -Path $envPath -Value $envContent

Write-Host "SQLite setup completed successfully."
Write-Host "You can now run the backend application with SQLite instead of PostgreSQL."