# Simple SQLite to PostgreSQL Migration for Law-GPT
param(
    [string]$PostgreSQLUrl = "NEED_POSTGRES_URL"
)

Write-Host "🗄️  SQLite to PostgreSQL Migration Guide" -ForegroundColor Green
Write-Host ""

# Check if SQLite database exists
if (Test-Path "data/lawgpt.db") {
    $fileSize = (Get-Item "data/lawgpt.db").Length / 1KB
    Write-Host "✅ Found SQLite database: data/lawgpt.db ($([math]::Round($fileSize, 2)) KB)" -ForegroundColor Green
} else {
    Write-Host "❌ SQLite database not found at data/lawgpt.db" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎯 Choose Your Migration Method:" -ForegroundColor Cyan
Write-Host ""

Write-Host "📝 Method 1: Create Fresh Database (Recommended)" -ForegroundColor Yellow
Write-Host "   ✅ Fastest and simplest" -ForegroundColor Green
Write-Host "   ✅ App will recreate tables automatically" -ForegroundColor Green
Write-Host "   ❌ Loses existing data" -ForegroundColor Red
Write-Host ""
Write-Host "   Steps:" -ForegroundColor White
Write-Host "   1. Create PostgreSQL service in Render" -ForegroundColor Gray
Write-Host "   2. Copy DATABASE_URL to backend environment" -ForegroundColor Gray
Write-Host "   3. Redeploy backend" -ForegroundColor Gray
Write-Host ""

Write-Host "🔄 Method 2: Migrate Data with TablePlus" -ForegroundColor Yellow
Write-Host "   ✅ Preserves your data" -ForegroundColor Green
Write-Host "   ✅ Visual interface" -ForegroundColor Green
Write-Host "   ⚠️  Requires TablePlus" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Steps:" -ForegroundColor White
Write-Host "   1. Open TablePlus" -ForegroundColor Gray
Write-Host "   2. Connect to SQLite: data/lawgpt.db" -ForegroundColor Gray
Write-Host "   3. Export → SQL Dump → Save as lawgpt_backup.sql" -ForegroundColor Gray
Write-Host "   4. Create PostgreSQL in Render" -ForegroundColor Gray
Write-Host "   5. Connect TablePlus to PostgreSQL" -ForegroundColor Gray
Write-Host "   6. Import → lawgpt_backup.sql" -ForegroundColor Gray

Write-Host ""
Write-Host "🚀 Quick Setup (Method 1):" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Create PostgreSQL in Render:" -ForegroundColor White
Write-Host "   • Go to https://dashboard.render.com" -ForegroundColor Gray
Write-Host "   • New + → PostgreSQL" -ForegroundColor Gray
Write-Host "   • Name: law-gpt-database" -ForegroundColor Gray
Write-Host "   • Plan: Free" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Copy Internal Database URL (looks like):" -ForegroundColor White
Write-Host "   postgresql://lawgpt:abc123@internal-host:5432/lawgpt" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Update backend environment:" -ForegroundColor White
Write-Host "   • Go to backend service → Environment" -ForegroundColor Gray
Write-Host "   • Add: DATABASE_URL=postgresql://..." -ForegroundColor Gray
Write-Host ""
Write-Host "4. Redeploy backend and test:" -ForegroundColor White
Write-Host "   curl https://law-gpt-backend-gr62.onrender.com/health/detailed" -ForegroundColor Gray

Write-Host ""
Write-Host "💡 Pro Tip: For a new app, Method 1 is perfectly fine!" -ForegroundColor Blue
Write-Host "   Your app will automatically create all necessary tables." -ForegroundColor Gray
