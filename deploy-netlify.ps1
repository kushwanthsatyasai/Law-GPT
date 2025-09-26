# Netlify Deployment Script for Law-GPT
param(
    [Parameter(Mandatory=$true)]
    [string]$BackendUrl,
    [switch]$Production,
    [switch]$SkipBuild
)

Write-Host "🌐 Deploying Law-GPT to Netlify..." -ForegroundColor Green

# Check if netlify CLI is installed
try {
    netlify --version | Out-Null
} catch {
    Write-Host "❌ Netlify CLI not found!" -ForegroundColor Red
    Write-Host "📦 Installing Netlify CLI..." -ForegroundColor Blue
    npm install -g netlify-cli
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install Netlify CLI!" -ForegroundColor Red
        exit 1
    }
}

# Validate backend URL
if ($BackendUrl -notmatch '^https?://') {
    Write-Host "❌ Backend URL must start with http:// or https://" -ForegroundColor Red
    Write-Host "   Example: https://your-app.railway.app" -ForegroundColor Yellow
    exit 1
}

Write-Host "🔧 Configuration:" -ForegroundColor Blue
Write-Host "   Backend URL: $BackendUrl" -ForegroundColor White
Write-Host "   Production: $($Production ? 'Yes' : 'No')" -ForegroundColor White
Write-Host "   Skip Build: $($SkipBuild ? 'Yes' : 'No')" -ForegroundColor White

# Update netlify.toml with backend URL
Write-Host "📝 Updating netlify.toml configuration..." -ForegroundColor Blue
$netlifyConfig = Get-Content "netlify.toml" -Raw
$netlifyConfig = $netlifyConfig -replace "https://your-backend-url\.railway\.app", $BackendUrl
Set-Content "netlify.toml" $netlifyConfig

# Check if user is logged in to Netlify
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

# Build the frontend
if (-not $SkipBuild) {
    Write-Host "🔨 Building frontend..." -ForegroundColor Blue
    Set-Location "frontend"
    
    Write-Host "   Installing dependencies..." -ForegroundColor Yellow
    npm ci
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies!" -ForegroundColor Red
        exit 1
    }
    
    # Set environment variable for build
    $env:VITE_API_BASE_URL = $BackendUrl
    
    Write-Host "   Building React app..." -ForegroundColor Yellow
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Build failed!" -ForegroundColor Red
        exit 1
    }
    
    Set-Location ".."
    Write-Host "✅ Frontend built successfully!" -ForegroundColor Green
}

# Deploy to Netlify
Write-Host "🚀 Deploying to Netlify..." -ForegroundColor Blue

if ($Production) {
    netlify deploy --prod --dir="frontend/dist"
} else {
    netlify deploy --dir="frontend/dist"
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Set environment variables in Netlify dashboard:" -ForegroundColor White
Write-Host "      - VITE_API_BASE_URL = $BackendUrl" -ForegroundColor Yellow
Write-Host "   2. Test your application" -ForegroundColor White
Write-Host "   3. Configure custom domain (optional)" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Useful links:" -ForegroundColor Cyan
Write-Host "   - Netlify Dashboard: https://app.netlify.com" -ForegroundColor White
Write-Host "   - Site Settings: Configure environment variables" -ForegroundColor White
Write-Host "   - Domain Settings: Add custom domain" -ForegroundColor White
Write-Host ""
