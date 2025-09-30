# Complete Deployment Script for Law-GPT
# Backend: Render | Frontend: Netlify | Database: PostgreSQL

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Law-GPT Production Deployment" -ForegroundColor Cyan
Write-Host "  Backend: Render | Frontend: Netlify" -ForegroundColor Cyan
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
        Write-Host "You can continue anyway and migrate later." -ForegroundColor Yellow
    }
} else {
    Write-Host "⏭️  Skipping data migration..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press Enter to continue..." -ForegroundColor Gray
Read-Host

# Step 2: Generate Environment Variables
Write-Host ""
Write-Host "🔐 Step 2: Environment Variables" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""

# Generate SECRET_KEY
$secretKey = python -c "import secrets; print(secrets.token_urlsafe(32))"
Write-Host "✅ Generated new SECRET_KEY" -ForegroundColor Green

# Get Google API Key from .env
$googleKey = (Get-Content .env -ErrorAction SilentlyContinue | Select-String "^GOOGLE_API_KEY=").ToString().Split('=')[1]
if (-not $googleKey -or $googleKey -eq "your_google_gemini_api_key_here") {
    Write-Host "⚠️  Google API key not found in .env" -ForegroundColor Yellow
    Write-Host "Enter your Google Gemini API key:" -ForegroundColor White
    $googleKey = Read-Host
}

Write-Host ""
Write-Host "📋 COPY THESE TO RENDER DASHBOARD:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""
Write-Host "DATABASE_URL=$POSTGRES_URL" -ForegroundColor White
Write-Host ""
Write-Host "GOOGLE_API_KEY=$googleKey" -ForegroundColor White
Write-Host ""
Write-Host "SECRET_KEY=$secretKey" -ForegroundColor White
Write-Host ""
Write-Host "ACCESS_TOKEN_EXPIRE_MINUTES=60" -ForegroundColor White
Write-Host "STORAGE_DIR=/data/uploads" -ForegroundColor White
Write-Host "APP_ENV=production" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""

# Save to file for reference
$envContent = @"
DATABASE_URL=$POSTGRES_URL
GOOGLE_API_KEY=$googleKey
SECRET_KEY=$secretKey
ACCESS_TOKEN_EXPIRE_MINUTES=60
STORAGE_DIR=/data/uploads
APP_ENV=production
"@
$envContent | Out-File -FilePath "RENDER_ENV_VARS.txt" -Encoding ASCII
Write-Host "✅ Environment variables saved to RENDER_ENV_VARS.txt" -ForegroundColor Green
Write-Host ""
Write-Host "Press Enter when you've added these to Render Dashboard..." -ForegroundColor Yellow
Read-Host

# Step 3: Deploy Backend
Write-Host ""
Write-Host "🚀 Step 3: Deploy Backend to Render" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""
Write-Host "1. Go to: https://dashboard.render.com/new/web" -ForegroundColor White
Write-Host "2. Connect your GitHub repository" -ForegroundColor White
Write-Host "3. Configure:" -ForegroundColor White
Write-Host "   - Name: law-gpt-backend" -ForegroundColor Gray
Write-Host "   - Root Directory: backend" -ForegroundColor Gray
Write-Host "   - Runtime: Python 3" -ForegroundColor Gray
Write-Host "   - Build: pip install -r requirements.txt" -ForegroundColor Gray
Write-Host "   - Start: uvicorn app.main:app --host 0.0.0.0 --port `$PORT" -ForegroundColor Gray
Write-Host "4. Add environment variables (from above)" -ForegroundColor White
Write-Host "5. Click 'Create Web Service'" -ForegroundColor White
Write-Host ""
Write-Host "What is your Render backend URL?" -ForegroundColor Yellow
Write-Host "(e.g., https://law-gpt-backend.onrender.com)" -ForegroundColor Gray
$backendUrl = Read-Host

if (-not $backendUrl) {
    $backendUrl = "https://law-gpt-backend.onrender.com"
    Write-Host "Using default: $backendUrl" -ForegroundColor Gray
}

# Create frontend env file
Write-Host ""
Write-Host "Creating frontend environment configuration..." -ForegroundColor Cyan
"VITE_API_BASE_URL=$backendUrl" | Out-File -FilePath "frontend\.env.production" -Encoding ASCII
Write-Host "✅ Created frontend/.env.production" -ForegroundColor Green

# Step 4: Deploy Frontend
Write-Host ""
Write-Host "🌐 Step 4: Deploy Frontend to Netlify" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""
Write-Host "Choose deployment method:" -ForegroundColor White
Write-Host "  1. Netlify CLI (faster)" -ForegroundColor Gray
Write-Host "  2. Netlify Dashboard (easier)" -ForegroundColor Gray
$method = Read-Host "Enter 1 or 2"

if ($method -eq "1") {
    Write-Host ""
    Write-Host "Deploying with Netlify CLI..." -ForegroundColor Cyan
    Write-Host ""
    
    # Check if Netlify CLI is installed
    $netlifyInstalled = Get-Command netlify -ErrorAction SilentlyContinue
    if (-not $netlifyInstalled) {
        Write-Host "Installing Netlify CLI..." -ForegroundColor Yellow
        npm install -g netlify-cli
    }
    
    Write-Host "Logging in to Netlify..." -ForegroundColor Cyan
    netlify login
    
    Write-Host ""
    Write-Host "Deploying to Netlify..." -ForegroundColor Cyan
    Set-Location frontend
    netlify deploy --prod --build
    Set-Location ..
    
    Write-Host ""
    Write-Host "✅ Deployment complete!" -ForegroundColor Green
    Write-Host "Check Netlify output above for your site URL" -ForegroundColor White
    
} else {
    Write-Host ""
    Write-Host "📝 Manual Deployment Steps:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Go to: https://app.netlify.com/start" -ForegroundColor White
    Write-Host "2. Click 'Import an existing project'" -ForegroundColor White
    Write-Host "3. Choose GitHub and select your repository" -ForegroundColor White
    Write-Host "4. Configure:" -ForegroundColor White
    Write-Host "   - Base directory: frontend" -ForegroundColor Gray
    Write-Host "   - Build command: npm run build" -ForegroundColor Gray
    Write-Host "   - Publish directory: frontend/dist" -ForegroundColor Gray
    Write-Host "5. Add Environment Variable:" -ForegroundColor White
    Write-Host "   VITE_API_BASE_URL=$backendUrl" -ForegroundColor Gray
    Write-Host "6. Click 'Deploy site'" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "What is your Netlify URL?" -ForegroundColor Yellow
Write-Host "(e.g., https://law-gpt.netlify.app)" -ForegroundColor Gray
$frontendUrl = Read-Host

# Step 5: Update CORS
Write-Host ""
Write-Host "🔧 Step 5: Update Backend CORS" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  Important: Update CORS in backend/app/main.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "Change the allow_origins to include:" -ForegroundColor White
Write-Host "  '$frontendUrl'" -ForegroundColor Cyan
Write-Host ""
Write-Host "Example:" -ForegroundColor Gray
Write-Host @"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "$frontendUrl",
        "https://*.netlify.app",
    ],
    ...
)
"@ -ForegroundColor White
Write-Host ""
Write-Host "After updating, commit and push to trigger Render redeploy:" -ForegroundColor Yellow
Write-Host "  git add backend/app/main.py" -ForegroundColor Gray
Write-Host "  git commit -m 'Update CORS for Netlify'" -ForegroundColor Gray
Write-Host "  git push origin main" -ForegroundColor Gray
Write-Host ""

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your Law-GPT is deployed at:" -ForegroundColor White
Write-Host ""
Write-Host "  Frontend:  $frontendUrl" -ForegroundColor Cyan
Write-Host "  Backend:   $backendUrl" -ForegroundColor Cyan
Write-Host "  API Docs:  $backendUrl/docs" -ForegroundColor Cyan
Write-Host "  Database:  PostgreSQL on Render ✅" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Environment variables saved to: RENDER_ENV_VARS.txt" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Update CORS in backend/app/main.py (see above)" -ForegroundColor White
Write-Host "  2. Push changes to trigger Render redeploy" -ForegroundColor White
Write-Host "  3. Test your deployment at $frontendUrl" -ForegroundColor White
Write-Host "  4. Register a new user and try features" -ForegroundColor White
Write-Host "  5. Monitor logs in Render/Netlify dashboards" -ForegroundColor White
Write-Host ""
Write-Host "🎊 Congratulations! Your app is live!" -ForegroundColor Green
Write-Host ""

# Create deployment summary file
$summary = @"
Law-GPT Deployment Summary
==========================

Deployed: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

Frontend: $frontendUrl
Backend:  $backendUrl
Database: PostgreSQL on Render

Environment Variables (backend):
- See RENDER_ENV_VARS.txt

Next Steps:
1. Update CORS in backend/app/main.py with Netlify URL
2. Push changes to GitHub
3. Test deployment
4. Monitor logs in dashboards

Dashboard Links:
- Render: https://dashboard.render.com
- Netlify: https://app.netlify.com
"@

$summary | Out-File -FilePath "DEPLOYMENT_SUMMARY.txt" -Encoding ASCII
Write-Host "📄 Deployment summary saved to: DEPLOYMENT_SUMMARY.txt" -ForegroundColor Green
Write-Host ""
