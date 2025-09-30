# Render + Netlify Deployment Script for Law-GPT
param(
    [string]$RenderUrl,
    [switch]$SkipRender,
    [switch]$SkipNetlify,
    [switch]$Production
)

Write-Host "🚀 Deploying Law-GPT to Render + Netlify..." -ForegroundColor Green

# If no Render URL provided, show instructions
if (-not $RenderUrl -and -not $SkipRender) {
    Write-Host ""
    Write-Host "🔧 STEP 1: Deploy Backend to Render" -ForegroundColor Cyan
    Write-Host "1. Go to https://render.com and sign up" -ForegroundColor White
    Write-Host "2. Connect your GitHub repository" -ForegroundColor White
    Write-Host "3. Create a Web Service:" -ForegroundColor White
    Write-Host "   - Name: law-gpt-backend" -ForegroundColor Yellow
    Write-Host "   - Root Directory: backend" -ForegroundColor Yellow
    Write-Host "   - Runtime: Docker" -ForegroundColor Yellow
    Write-Host "   - Dockerfile Path: ./Dockerfile" -ForegroundColor Yellow
    Write-Host "4. Add environment variables:" -ForegroundColor White
    Write-Host "   - GOOGLE_API_KEY=your_google_api_key" -ForegroundColor Yellow
    Write-Host "   - INDIAN_KANOON_API_KEY=your_indian_kanoon_api_key" -ForegroundColor Yellow
    Write-Host "   - SECRET_KEY=your_secret_key" -ForegroundColor Yellow
    Write-Host "5. Create PostgreSQL database and add DATABASE_URL" -ForegroundColor White
    Write-Host "6. Deploy and copy your Render URL" -ForegroundColor White
    Write-Host ""
    Write-Host "Then run this script with your Render URL:" -ForegroundColor Cyan
    Write-Host ".\deploy-render-netlify.ps1 -RenderUrl 'https://your-app.onrender.com'" -ForegroundColor Yellow
    Write-Host ""
    
    if (-not $SkipNetlify) {
        exit 0
    }
}

# Validate Render URL format
if ($RenderUrl -and $RenderUrl -notmatch '^https?://.*\.onrender\.com/?$') {
    Write-Host "⚠️  Render URL should be in format: https://your-app.onrender.com" -ForegroundColor Yellow
    Write-Host "   You provided: $RenderUrl" -ForegroundColor White
}

# Deploy Backend to Render (Instructions)
if (-not $SkipRender) {
    Write-Host ""
    Write-Host "🔧 Backend Deployment to Render" -ForegroundColor Blue
    
    if ($RenderUrl) {
        Write-Host "✅ Using Render URL: $RenderUrl" -ForegroundColor Green
        
        # Test Render backend
        Write-Host "🏥 Testing Render backend health..." -ForegroundColor Yellow
        try {
            $response = Invoke-WebRequest -Uri "$RenderUrl/health" -TimeoutSec 10 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Render backend is healthy!" -ForegroundColor Green
            }
        } catch {
            Write-Host "⚠️  Render backend not responding (this is OK if still deploying)" -ForegroundColor Yellow
            Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "📋 Render deployment checklist:" -ForegroundColor Yellow
        Write-Host "   □ Repository connected to Render" -ForegroundColor White
        Write-Host "   □ Root directory set to 'backend'" -ForegroundColor White
        Write-Host "   □ Runtime set to 'Docker'" -ForegroundColor White
        Write-Host "   □ Environment variables configured" -ForegroundColor White
        Write-Host "   □ PostgreSQL database created" -ForegroundColor White
    }
}

# Deploy Frontend to Netlify
if (-not $SkipNetlify) {
    Write-Host ""
    Write-Host "🌐 Frontend Deployment to Netlify" -ForegroundColor Blue
    
    # Check if netlify CLI is available
    try {
        netlify --version | Out-Null
    } catch {
        Write-Host "📦 Installing Netlify CLI..." -ForegroundColor Yellow
        npm install -g netlify-cli
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to install Netlify CLI!" -ForegroundColor Red
            Write-Host "   Please install manually: npm install -g netlify-cli" -ForegroundColor Yellow
            exit 1
        }
    }
    
    # Update netlify.toml with Render URL
    if ($RenderUrl) {
        Write-Host "📝 Updating netlify.toml with Render URL..." -ForegroundColor Yellow
        $netlifyConfig = Get-Content "netlify.toml" -Raw
        $netlifyConfig = $netlifyConfig -replace "https://your-backend-url\.onrender\.com", $RenderUrl.TrimEnd('/')
        Set-Content "netlify.toml" $netlifyConfig
        Write-Host "✅ netlify.toml updated!" -ForegroundColor Green
    }
    
    # Check Netlify login
    try {
        netlify status | Out-Null
    } catch {
        Write-Host "🔐 Please log in to Netlify..." -ForegroundColor Yellow
        netlify login
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to log in to Netlify!" -ForegroundColor Red
            exit 1
        }
    }
    
    # Build frontend
    Write-Host "🔨 Building frontend..." -ForegroundColor Yellow
    Set-Location "frontend"
    
    # Install dependencies
    Write-Host "   Installing dependencies..." -ForegroundColor Gray
    npm ci
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies!" -ForegroundColor Red
        exit 1
    }
    
    # Set environment variable for build
    if ($RenderUrl) {
        $env:VITE_API_BASE_URL = $RenderUrl.TrimEnd('/')
    }
    
    # Build the app
    Write-Host "   Building React application..." -ForegroundColor Gray
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Build failed!" -ForegroundColor Red
        exit 1
    }
    
    Set-Location ".."
    
    # Deploy to Netlify
    Write-Host "🚀 Deploying to Netlify..." -ForegroundColor Yellow
    
    if ($Production) {
        netlify deploy --prod --dir="frontend/dist"
    } else {
        netlify deploy --dir="frontend/dist"
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Netlify deployment failed!" -ForegroundColor Red
        exit 1
    }
}

# Success message
Write-Host ""
Write-Host "🎉 Deployment Process Complete!" -ForegroundColor Green
Write-Host ""

if ($RenderUrl) {
    Write-Host "📱 Your Application URLs:" -ForegroundColor Cyan
    Write-Host "   🔧 Backend (Render): $RenderUrl" -ForegroundColor White
    Write-Host "   🌐 Frontend (Netlify): Check Netlify dashboard for URL" -ForegroundColor White
    Write-Host ""
    
    Write-Host "🔍 Test Your Deployment:" -ForegroundColor Cyan
    Write-Host "   Backend Health: $RenderUrl/health" -ForegroundColor White
    Write-Host "   API Docs: $RenderUrl/docs" -ForegroundColor White
    Write-Host ""
}

Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Test all application features" -ForegroundColor White
Write-Host "   2. Set up custom domains" -ForegroundColor White
Write-Host "   3. Monitor logs and performance" -ForegroundColor White
Write-Host "   4. Configure production API keys" -ForegroundColor White
Write-Host ""

Write-Host "🔗 Useful Links:" -ForegroundColor Cyan
Write-Host "   - Render Dashboard: https://dashboard.render.com" -ForegroundColor White
Write-Host "   - Netlify Dashboard: https://app.netlify.com" -ForegroundColor White
Write-Host "   - Deployment Guide: RENDER_NETLIFY_DEPLOYMENT.md" -ForegroundColor White
Write-Host ""
