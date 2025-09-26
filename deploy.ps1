# Law-GPT Production Deployment Script for Windows
param(
    [switch]$SkipHealthCheck,
    [switch]$Force
)

Write-Host "🚀 Starting Law-GPT deployment..." -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "📝 Please copy .env.example to .env and configure your API keys:" -ForegroundColor Yellow
    Write-Host "   Copy-Item .env.example .env" -ForegroundColor Cyan
    Write-Host "   Edit .env with your actual API keys and configuration" -ForegroundColor Cyan
    exit 1
}

# Check for required environment variables
Write-Host "🔍 Checking required environment variables..." -ForegroundColor Blue

function Check-EnvVar {
    param($VarName)
    $content = Get-Content .env -Raw
    if ($content -match "^$VarName=(.+)$" -and $Matches[1] -notmatch "your_.*_key.*") {
        Write-Host "✅ $VarName is set" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ $VarName is not properly configured in .env" -ForegroundColor Red
        return $false
    }
}

$missingVars = $false

# Check required API keys
if (-not (Check-EnvVar "GOOGLE_API_KEY")) { $missingVars = $true }
if (-not (Check-EnvVar "SECRET_KEY")) { $missingVars = $true }

# Check Indian Kanoon API key
$content = Get-Content .env -Raw
if ($content -match "^INDIAN_KANOON_API_KEY=(.+)$" -and $Matches[1] -notmatch "your_.*_key.*") {
    Write-Host "✅ INDIAN_KANOON_API_KEY is set" -ForegroundColor Green
} else {
    Write-Host "⚠️  INDIAN_KANOON_API_KEY is not set - Indian legal database features will use mock data" -ForegroundColor Yellow
}

if ($missingVars -and -not $Force) {
    Write-Host "❌ Please configure the missing environment variables in .env file" -ForegroundColor Red
    Write-Host "   Use -Force to deploy anyway with mock data" -ForegroundColor Yellow
    exit 1
}

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Blue
New-Item -ItemType Directory -Force -Path "uploads", "data", "ssl" | Out-Null

# Check if Docker is running
try {
    docker version | Out-Null
} catch {
    Write-Host "❌ Docker is not running or not installed!" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop and try again" -ForegroundColor Yellow
    exit 1
}

# Check if docker-compose is available
try {
    docker-compose --version | Out-Null
} catch {
    Write-Host "❌ docker-compose is not available!" -ForegroundColor Red
    Write-Host "   Please install Docker Compose and try again" -ForegroundColor Yellow
    exit 1
}

# Build and start services
Write-Host "🔨 Building Docker images..." -ForegroundColor Blue
docker-compose build --no-cache
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "🗄️  Starting database..." -ForegroundColor Blue
docker-compose up -d db
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start database!" -ForegroundColor Red
    exit 1
}

Write-Host "⏳ Waiting for database to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "🚀 Starting all services..." -ForegroundColor Blue
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start services!" -ForegroundColor Red
    Write-Host "📊 Checking logs..." -ForegroundColor Blue
    docker-compose logs
    exit 1
}

Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Health check
if (-not $SkipHealthCheck) {
    Write-Host "🏥 Performing health checks..." -ForegroundColor Blue
    $maxAttempts = 30
    $attempt = 1

    while ($attempt -le $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Backend is healthy!" -ForegroundColor Green
                break
            }
        } catch {
            Write-Host "⏳ Waiting for backend... (attempt $attempt/$maxAttempts)" -ForegroundColor Yellow
            Start-Sleep -Seconds 5
            $attempt++
        }
    }

    if ($attempt -gt $maxAttempts) {
        Write-Host "❌ Backend health check failed!" -ForegroundColor Red
        Write-Host "📊 Checking logs..." -ForegroundColor Blue
        docker-compose logs backend
        exit 1
    }

    # Check frontend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Frontend is healthy!" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️  Frontend might be starting up, check http://localhost:3000" -ForegroundColor Yellow
    }

    # Check nginx
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:80" -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Nginx is healthy!" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️  Nginx might be starting up, check http://localhost" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🎉 Law-GPT deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Access your application:" -ForegroundColor Cyan
Write-Host "   🌐 Main application: http://localhost" -ForegroundColor White
Write-Host "   🎯 Direct frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   🔧 Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   📊 Health check: http://localhost:8000/health/detailed" -ForegroundColor White
Write-Host ""
Write-Host "📋 To view logs:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f backend" -ForegroundColor White
Write-Host "   docker-compose logs -f frontend" -ForegroundColor White
Write-Host "   docker-compose logs -f nginx" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop:" -ForegroundColor Cyan
Write-Host "   docker-compose down" -ForegroundColor White
Write-Host ""
Write-Host "🔧 To rebuild and restart:" -ForegroundColor Cyan
Write-Host "   docker-compose down; .\deploy.ps1" -ForegroundColor White
Write-Host ""

# Show current status
Write-Host "📊 Current service status:" -ForegroundColor Blue
docker-compose ps
