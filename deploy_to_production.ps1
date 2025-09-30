# Complete Deployment Script for Law-GPT
# Backend: Render | Frontend: Vercel | Database: PostgreSQL

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Law-GPT Production Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$POSTGRES_URL = "postgresql://lawgpt_user:rQ1FLdtndZu9bDejYfHzm2SIyYxGKvhZ@dpg-d3bcnkvfte5s739l6lq0-a.oregon-postgres.render.com/lawgpt"

# Step 1: Migrate Data
Write-Host "📊 Step 1: Migrate Data to PostgreSQL" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""
Write-Host "Do you want to migrate your SQLite data to PostgreSQL? (y/n)" -ForegroundColor White
$migrate = Read-Host

if ($migrate -eq "y") {
    Write-Host ""
    Write-Host "🔄 Migrating data..." -ForegroundColor Cyan
    $env:DATABASE_URL = $POSTGRES_URL
    python scripts\migrate_sqlite_to_postgres.py $POSTGRES_URL
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Data migration completed!" -ForegroundColor Green
    } else {
        Write-Host "❌ Migration failed. Check errors above." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⏭️  Skipping data migration..." -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Git Setup
Write-Host "📦 Step 2: Prepare Git Repository" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""
Write-Host "Make sure your code is committed to Git:" -ForegroundColor White
Write-Host ""
Write-Host "  git add ." -ForegroundColor Gray
Write-Host "  git commit -m 'Deploy to production with PostgreSQL'" -ForegroundColor Gray
Write-Host "  git push origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Enter when ready to continue..." -ForegroundColor Yellow
Read-Host

# Step 3: Backend Environment Variables
Write-Host ""
Write-Host "🔐 Step 3: Backend Environment Variables" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""
Write-Host "Copy these environment variables to Render Dashboard:" -ForegroundColor White
Write-Host ""
Write-Host "DATABASE_URL=$POSTGRES_URL" -ForegroundColor Cyan
Write-Host ""

# Generate SECRET_KEY
$secretKey = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
Write-Host "SECRET_KEY=$secretKey" -ForegroundColor Cyan
Write-Host ""

# Get Google API Key from .env
$googleKey = (Get-Content .env | Select-String "^GOOGLE_API_KEY=").ToString().Split('=')[1]
Write-Host "GOOGLE_API_KEY=$googleKey" -ForegroundColor Cyan
Write-Host ""

Write-Host "ACCESS_TOKEN_EXPIRE_MINUTES=60" -ForegroundColor Cyan
Write-Host "STORAGE_DIR=/data/uploads" -ForegroundColor Cyan
Write-Host "APP_ENV=production" -ForegroundColor Cyan
Write-Host ""
Write-Host "Copy these values and paste them in Render Dashboard!" -ForegroundColor Yellow
Write-Host "Press Enter when done..." -ForegroundColor Yellow
Read-Host

# Step 4: Deploy Backend
Write-Host ""
Write-Host "🚀 Step 4: Deploy Backend to Render" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""
Write-Host "1. Go to: https://dashboard.render.com" -ForegroundColor White
Write-Host "2. Click 'New +' → 'Blueprint'" -ForegroundColor White
Write-Host "3. Connect your GitHub repository" -ForegroundColor White
Write-Host "4. Render will detect render.yaml" -ForegroundColor White
Write-Host "5. Add environment variables (from above)" -ForegroundColor White
Write-Host "6. Click 'Apply' to deploy" -ForegroundColor White
Write-Host ""
Write-Host "What is your Render backend URL?" -ForegroundColor Yellow
Write-Host "(e.g., https://law-gpt-backend.onrender.com)" -ForegroundColor Gray
$backendUrl = Read-Host

# Step 5: Deploy Frontend
Write-Host ""
Write-Host "🌐 Step 5: Deploy Frontend to Vercel" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""

# Update frontend env for Vercel
Write-Host "Creating frontend environment file..." -ForegroundColor Cyan
"VITE_API_BASE_URL=$backendUrl" | Out-File -FilePath "frontend\.env.production" -Encoding ASCII

Write-Host ""
Write-Host "Option 1: Vercel CLI (Recommended)" -ForegroundColor White
Write-Host "  cd frontend" -ForegroundColor Gray
Write-Host "  vercel --prod" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 2: Vercel Dashboard" -ForegroundColor White
Write-Host "  1. Go to: https://vercel.com/new" -ForegroundColor Gray
Write-Host "  2. Import your GitHub repository" -ForegroundColor Gray
Write-Host "  3. Root Directory: 'frontend'" -ForegroundColor Gray
Write-Host "  4. Framework: Vite" -ForegroundColor Gray
Write-Host "  5. Environment Variable: VITE_API_BASE_URL=$backendUrl" -ForegroundColor Gray
Write-Host "  6. Click 'Deploy'" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Enter when frontend is deployed..." -ForegroundColor Yellow
Read-Host

# Step 6: Final Configuration
Write-Host ""
Write-Host "✅ Step 6: Final Configuration" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""
Write-Host "What is your Vercel frontend URL?" -ForegroundColor Yellow
Write-Host "(e.g., https://law-gpt.vercel.app)" -ForegroundColor Gray
$frontendUrl = Read-Host

Write-Host ""
Write-Host "📝 Update backend CORS:" -ForegroundColor Cyan
Write-Host "  Edit backend/app/main.py" -ForegroundColor White
Write-Host "  Change allow_origins to:" -ForegroundColor White
Write-Host "    '$frontendUrl'" -ForegroundColor Gray
Write-Host ""
Write-Host "  Then commit and push to trigger Render redeploy" -ForegroundColor White
Write-Host ""

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your Law-GPT is deployed at:" -ForegroundColor White
Write-Host "  Frontend: $frontendUrl" -ForegroundColor Cyan
Write-Host "  Backend:  $backendUrl" -ForegroundColor Cyan
Write-Host "  Database: PostgreSQL on Render" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Test your deployment" -ForegroundColor White
Write-Host "  2. Register a new user" -ForegroundColor White
Write-Host "  3. Try all features" -ForegroundColor White
Write-Host "  4. Monitor logs in Render/Vercel dashboards" -ForegroundColor White
Write-Host ""
Write-Host "🎊 Congratulations! Your app is live!" -ForegroundColor Green
Write-Host ""
