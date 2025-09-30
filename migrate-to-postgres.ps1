# SQLite to PostgreSQL Migration Script for Law-GPT
param(
    [Parameter(Mandatory=$true)]
    [string]$PostgreSQLUrl,
    [string]$SqliteFile = "data/lawgpt.db",
    [switch]$DryRun
)

Write-Host "🔄 Migrating SQLite to PostgreSQL..." -ForegroundColor Green

# Check if SQLite file exists
if (-not (Test-Path $SqliteFile)) {
    Write-Host "❌ SQLite database not found: $SqliteFile" -ForegroundColor Red
    Write-Host "💡 Available database files:" -ForegroundColor Yellow
    Get-ChildItem -Path "." -Name "*.db" -Recurse | ForEach-Object {
        Write-Host "   - $_" -ForegroundColor White
    }
    exit 1
}

Write-Host "📊 SQLite database found: $SqliteFile" -ForegroundColor Green

# Check if we have sqlite3 command
try {
    sqlite3 -version | Out-Null
    $hasSqlite = $true
} catch {
    Write-Host "⚠️  sqlite3 command not found" -ForegroundColor Yellow
    $hasSqlite = $false
}

# Check if we have psql command
try {
    psql --version | Out-Null
    $hasPsql = $true
} catch {
    Write-Host "⚠️  psql command not found" -ForegroundColor Yellow
    $hasPsql = $false
}

Write-Host ""
Write-Host "🔧 Migration Options:" -ForegroundColor Cyan

if ($hasSqlite -and $hasPsql) {
    Write-Host "✅ Option A: Direct command-line migration (recommended)" -ForegroundColor Green
    Write-Host ""
    
    if ($DryRun) {
        Write-Host "🔍 DRY RUN - Commands that would be executed:" -ForegroundColor Yellow
        Write-Host "   sqlite3 $SqliteFile .dump > dump.sql" -ForegroundColor Gray
        Write-Host "   psql '$PostgreSQLUrl' -f dump.sql" -ForegroundColor Gray
    } else {
        Write-Host "📤 Exporting SQLite data..." -ForegroundColor Blue
        sqlite3 $SqliteFile .dump > dump.sql
        
        if (Test-Path "dump.sql") {
            Write-Host "✅ SQLite export completed: dump.sql" -ForegroundColor Green
            
            Write-Host "📥 Importing to PostgreSQL..." -ForegroundColor Blue
            try {
                psql $PostgreSQLUrl -f dump.sql
                Write-Host "✅ PostgreSQL import completed!" -ForegroundColor Green
                
                # Clean up
                Remove-Item "dump.sql"
                Write-Host "🧹 Cleaned up temporary files" -ForegroundColor Gray
            } catch {
                Write-Host "❌ PostgreSQL import failed: $($_.Exception.Message)" -ForegroundColor Red
                Write-Host "💡 Check connection string and try manual import" -ForegroundColor Yellow
            }
        } else {
            Write-Host "❌ SQLite export failed" -ForegroundColor Red
        }
    }
} else {
    Write-Host "📱 Option B: Manual migration using TablePlus/pgAdmin" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Steps:" -ForegroundColor Cyan
    Write-Host "1. Open TablePlus" -ForegroundColor White
    Write-Host "2. Connect to your SQLite database: $SqliteFile" -ForegroundColor White
    Write-Host "3. Export → SQL Dump" -ForegroundColor White
    Write-Host "4. Connect to PostgreSQL: $PostgreSQLUrl" -ForegroundColor White
    Write-Host "5. Import → SQL file" -ForegroundColor White
}

Write-Host ""
Write-Host "🗄️  Option C: Create PostgreSQL Service in Render" -ForegroundColor Cyan
Write-Host ""
Write-Host "Steps:" -ForegroundColor White
Write-Host "1. Go to https://dashboard.render.com" -ForegroundColor Gray
Write-Host "2. New + → PostgreSQL" -ForegroundColor Gray
Write-Host "3. Settings:" -ForegroundColor Gray
Write-Host "   - Name: law-gpt-database" -ForegroundColor Yellow
Write-Host "   - Database: lawgpt" -ForegroundColor Yellow
Write-Host "   - User: lawgpt" -ForegroundColor Yellow
Write-Host "   - Plan: Free (256MB, 1GB storage)" -ForegroundColor Yellow
Write-Host "4. Copy Internal Database URL" -ForegroundColor Gray
Write-Host "5. Add to backend environment: DATABASE_URL=..." -ForegroundColor Gray

Write-Host ""
Write-Host "📋 Next Steps After Migration:" -ForegroundColor Cyan
Write-Host "1. Update Render environment variable:" -ForegroundColor White
Write-Host "   DATABASE_URL=$PostgreSQLUrl" -ForegroundColor Yellow
Write-Host "2. Redeploy backend service" -ForegroundColor White
Write-Host "3. Test health endpoint: /health/detailed" -ForegroundColor White

Write-Host ""
Write-Host "💡 Pro Tip: If you don't have critical data, just create a fresh PostgreSQL database" -ForegroundColor Blue
Write-Host "   Your app will automatically create tables on first run" -ForegroundColor Gray
