# Law-GPT Deployment Guide

## 🚀 Production Deployment with Docker

This guide walks you through deploying Law-GPT as a production-ready website with full Indian Kanoon API integration.

## 📋 Prerequisites

- **Docker & Docker Compose** installed
- **Indian Kanoon API Key** (and other optional API keys)
- **Google Gemini API Key** (required for AI features)
- **Domain name** (for production deployment)
- **SSL Certificate** (for HTTPS - optional but recommended)

## 🔧 Quick Setup

### 1. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual API keys
nano .env  # or use any text editor
```

**Required Configuration:**
```env
# Security - CHANGE THIS IN PRODUCTION!
SECRET_KEY=your_super_secret_key_here_change_in_production

# AI API Keys (Required)
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Indian Legal Database API Keys
INDIAN_KANOON_API_KEY=your_indian_kanoon_api_key_here

# Database (PostgreSQL recommended for production)
DATABASE_URL=postgresql://lawgpt:lawgpt@db:5432/lawgpt
```

### 2. Deploy with One Command

**For Linux/macOS:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**For Windows:**
```powershell
.\deploy.ps1
```

### 3. Access Your Application

- **Main Application**: http://localhost
- **Backend API**: http://localhost:8000
- **Direct Frontend**: http://localhost:3000
- **Health Check**: http://localhost:8000/health/detailed

## 🏗️ Architecture Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Client   │───▶│    Nginx    │───▶│  Frontend   │    │  Backend    │
│  (Browser)  │    │ (Port 80)   │    │ (Port 3000) │    │ (Port 8000) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                           │                                      │
                           └──────────────────────────────────────┘
                                         │
                                  ┌─────────────┐
                                  │ PostgreSQL  │
                                  │ (Port 5432) │
                                  └─────────────┘
```

## 🔑 API Keys Configuration

### Indian Kanoon API Key

1. **Visit**: https://www.indiankanoon.org/api/
2. **Sign up** for an API account
3. **Get your API key**
4. **Add to .env**: `INDIAN_KANOON_API_KEY=your_key_here`

**Pricing**: ₹0.50 per search, ₹0.20 per document

### Google Gemini API Key

1. **Visit**: https://aistudio.google.com/app/apikey
2. **Create new API key**
3. **Add to .env**: `GOOGLE_API_KEY=your_key_here`

**Free Tier**: 15 requests per minute

### Optional API Keys

- **SCC Online**: For additional Indian legal data
- **OpenAI**: For alternative AI processing
- **CANLII**: For Canadian legal data

## 🗄️ Database Options

### PostgreSQL (Recommended)
```env
DATABASE_URL=postgresql://lawgpt:lawgpt@db:5432/lawgpt
```

### SQLite (Development)
```env
DATABASE_URL=sqlite:///./data/lawgpt.db
```

## 🔐 Production Security

### 1. SSL/HTTPS Setup

**For production with domain:**
```nginx
# Edit nginx.conf and uncomment HTTPS block
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    # ... SSL configuration
}
```

**Place SSL certificates in `./ssl/` directory**

### 2. Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Use strong database passwords
- [ ] Enable HTTPS with valid SSL certificates
- [ ] Configure firewall rules
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity

## 🌐 Domain Setup

### 1. DNS Configuration
Point your domain to your server's IP:
```
A    your-domain.com    → YOUR_SERVER_IP
A    www.your-domain.com → YOUR_SERVER_IP
```

### 2. Update nginx.conf
```nginx
server_name your-domain.com www.your-domain.com;
```

### 3. SSL Certificate (Let's Encrypt)
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/health/detailed
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx
```

### Service Management
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild and restart
docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

### Backup Database
```bash
# PostgreSQL backup
docker-compose exec db pg_dump -U lawgpt lawgpt > backup.sql

# Restore backup
docker-compose exec -T db psql -U lawgpt lawgpt < backup.sql
```

## 🚀 Cloud Deployment

### AWS EC2
1. Launch EC2 instance (t3.medium or larger)
2. Install Docker & Docker Compose
3. Clone repository
4. Configure .env with API keys
5. Run deployment script
6. Configure security groups (ports 80, 443)

### DigitalOcean Droplet
1. Create droplet with Docker pre-installed
2. Clone repository
3. Configure .env
4. Run deployment script
5. Configure firewall

### Google Cloud Platform
1. Create Compute Engine instance
2. Install Docker & Docker Compose
3. Clone repository and configure
4. Run deployment script
5. Configure firewall rules

## 🔧 Troubleshooting

### Common Issues

**1. API Key Errors**
```
Error: INDIAN_KANOON_API_KEY not found
```
- Solution: Ensure API key is properly set in .env file

**2. Database Connection Issues**
```
Error: Could not connect to database
```
- Solution: Wait for database to start (may take 30+ seconds)
- Check: `docker-compose logs db`

**3. Frontend Build Errors**
```
Error: npm run build failed
```
- Solution: Clear node_modules and rebuild
```bash
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d
```

**4. Nginx Configuration Errors**
```
Error: nginx configuration test failed
```
- Solution: Check nginx.conf syntax
```bash
docker-compose exec nginx nginx -t
```

### Performance Tuning

**1. Backend Workers**
Adjust worker count in `backend/Dockerfile`:
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**2. Database Connections**
Increase PostgreSQL connections in `docker-compose.yml`:
```yaml
environment:
  POSTGRES_MAX_CONNECTIONS: "200"
```

**3. Nginx Caching**
Add caching to `nginx.conf`:
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|svg|ico)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 📞 Support

For issues and questions:
- Check logs: `docker-compose logs -f`
- Health check: `http://localhost:8000/health/detailed`
- Indian Kanoon API Status: Check their documentation
- Google Gemini API Status: Check Google AI Studio

## 🎯 Next Steps

After successful deployment:
1. **Test all features** with real API keys
2. **Set up monitoring** and alerting
3. **Configure backups** for database and uploads
4. **Set up SSL certificates** for HTTPS
5. **Configure domain name** and DNS
6. **Set up CI/CD** for automated deployments

---

**🎉 Congratulations! Your Law-GPT application is now deployed and ready for production use with full Indian Kanoon API integration!**
