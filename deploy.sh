#!/bin/bash

# Law-GPT Production Deployment Script
set -e

echo "🚀 Starting Law-GPT deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Please copy .env.example to .env and configure your API keys:"
    echo "   cp .env.example .env"
    echo "   Edit .env with your actual API keys and configuration"
    exit 1
fi

# Check for required environment variables
echo "🔍 Checking required environment variables..."

# Function to check if a variable is set
check_env_var() {
    if grep -q "^$1=" .env && ! grep -q "^$1=.*your_.*_key.*" .env; then
        echo "✅ $1 is set"
    else
        echo "❌ $1 is not properly configured in .env"
        MISSING_VARS=true
    fi
}

MISSING_VARS=false

# Check required API keys
check_env_var "GOOGLE_API_KEY"
check_env_var "SECRET_KEY"

# Check Indian Kanoon API key
if grep -q "^INDIAN_KANOON_API_KEY=" .env && ! grep -q "^INDIAN_KANOON_API_KEY=.*your_.*_key.*" .env; then
    echo "✅ INDIAN_KANOON_API_KEY is set"
else
    echo "⚠️  INDIAN_KANOON_API_KEY is not set - Indian legal database features will use mock data"
fi

if [ "$MISSING_VARS" = true ]; then
    echo "❌ Please configure the missing environment variables in .env file"
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads data ssl

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build --no-cache

echo "🗄️  Starting database..."
docker-compose up -d db

echo "⏳ Waiting for database to be ready..."
sleep 10

echo "🚀 Starting all services..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 15

# Health check
echo "🏥 Performing health checks..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy!"
        break
    else
        echo "⏳ Waiting for backend... (attempt $attempt/$max_attempts)"
        sleep 5
        attempt=$((attempt + 1))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ Backend health check failed!"
    echo "📊 Checking logs..."
    docker-compose logs backend
    exit 1
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy!"
else
    echo "⚠️  Frontend might be starting up, check http://localhost:3000"
fi

# Check nginx
if curl -f http://localhost:80 > /dev/null 2>&1; then
    echo "✅ Nginx is healthy!"
else
    echo "⚠️  Nginx might be starting up, check http://localhost"
fi

echo ""
echo "🎉 Law-GPT deployment completed!"
echo ""
echo "📱 Access your application:"
echo "   🌐 Main application: http://localhost"
echo "   🎯 Direct frontend: http://localhost:3000"
echo "   🔧 Backend API: http://localhost:8000"
echo "   📊 Health check: http://localhost:8000/health/detailed"
echo ""
echo "📋 To view logs:"
echo "   docker-compose logs -f backend"
echo "   docker-compose logs -f frontend"
echo "   docker-compose logs -f nginx"
echo ""
echo "🛑 To stop:"
echo "   docker-compose down"
echo ""
echo "🔧 To rebuild and restart:"
echo "   docker-compose down && ./deploy.sh"
echo ""

# Show current status
echo "📊 Current service status:"
docker-compose ps
