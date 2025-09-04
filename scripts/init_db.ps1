# PostgreSQL initialization script for Law-GPT

# Check if PostgreSQL is installed
$pgVersion = (Get-Command psql -ErrorAction SilentlyContinue).Version
if (-not $pgVersion) {
    Write-Error "PostgreSQL is not installed or not in PATH. Please install PostgreSQL first."
    exit 1
}

# Database configuration
$POSTGRES_USER = "lawgpt"
$POSTGRES_PASSWORD = "lawgpt"
$POSTGRES_DB = "lawgpt"

# Create user if not exists
$userExists = psql -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$POSTGRES_USER'" 2>$null
if (-not $userExists) {
    Write-Host "Creating user $POSTGRES_USER..."
    psql -U postgres -c "CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create user. Make sure you have PostgreSQL admin rights."
        exit 1
    }
}

# Create database if not exists
$dbExists = psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$POSTGRES_DB'" 2>$null
if (-not $dbExists) {
    Write-Host "Creating database $POSTGRES_DB..."
    psql -U postgres -c "CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER;" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create database."
        exit 1
    }
}

# Grant privileges
Write-Host "Granting privileges..."
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;" 2>$null

# Enable pgvector extension
Write-Host "Enabling pgvector extension..."
psql -U postgres -d $POSTGRES_DB -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>$null

Write-Host "Database initialization completed successfully."
Write-Host "You can now run the backend application."