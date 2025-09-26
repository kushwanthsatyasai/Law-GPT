# 🚂 Railway Deployment Fix for Law-GPT Backend

## 🔥 The Issue
Railway is looking for `/app/index.js` (Node.js) but your backend is Python-based. This happens when Railway auto-detects the wrong runtime.

## ✅ Solutions

### Solution 1: Deploy Backend Folder Only (Recommended)

1. **Create a separate repository for backend**:
   ```bash
   # Create new repo with just backend code
   mkdir law-gpt-backend
   cd law-gpt-backend
   
   # Copy backend files
   cp -r ../Law-GPT/backend/* .
   
   # Initialize git
   git init
   git add .
   git commit -m "Initial backend deployment"
   
   # Push to GitHub (create new repo first)
   git remote add origin https://github.com/yourusername/law-gpt-backend.git
   git push -u origin main
   ```

2. **Deploy the backend-only repo to Railway**:
   - Go to [railway.app](https://railway.app)
   - Create new project
   - Connect the `law-gpt-backend` repository
   - Railway will correctly detect Python/Dockerfile

### Solution 2: Fix Current Repository

1. **Update your Railway project settings**:
   - Go to your Railway project
   - Settings → Environment
   - Set **Root Directory**: `/backend`

2. **Or use Railway CLI to redeploy**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Navigate to backend folder
   cd backend
   
   # Link to your project
   railway link
   
   # Deploy from backend folder
   railway up
   ```

### Solution 3: Railway Configuration File

The `railway.json` files I created should fix the detection issue:

```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health"
  }
}
```

## 🔧 Environment Variables for Railway

Set these in your Railway project:

```env
# Required
GOOGLE_API_KEY=your_google_gemini_api_key
INDIAN_KANOON_API_KEY=your_indian_kanoon_api_key
SECRET_KEY=your_super_secret_key_change_this

# Database (Railway provides PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Optional
OPENAI_API_KEY=your_openai_key
SCC_ONLINE_API_KEY=your_scc_key
KANOON_DEV_API_KEY=your_kanoon_dev_key

# App settings
APP_ENV=production
STORAGE_DIR=/data/uploads
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## 🐳 Dockerfile Fixes

The updated `backend/Dockerfile` now:
- Uses `$PORT` environment variable (Railway requirement)
- Handles health checks properly
- Optimized for Railway deployment

## 🚀 Quick Fix Steps

**Option A: Redeploy with Root Directory**
1. Go to Railway project → Settings
2. Set Root Directory: `/backend`
3. Redeploy

**Option B: Use Backend-Only Repo**
1. Create new repo with just backend code
2. Deploy new repo to Railway
3. Update Netlify environment with new Railway URL

**Option C: Manual Railway CLI Deploy**
```bash
cd backend
railway login
railway link YOUR_PROJECT_ID
railway up
```

## 🔍 Troubleshooting

### Check Railway Logs
```bash
railway logs
```

### Common Issues

1. **Wrong runtime detected**:
   - Solution: Set Root Directory to `/backend`

2. **Port binding issues**:
   - Solution: Updated Dockerfile uses `$PORT` variable

3. **Health check fails**:
   - Solution: Disabled health check in Dockerfile (Railway handles this)

4. **Dependencies not found**:
   - Solution: Added gunicorn to requirements.txt

## 📱 Test Your Deployment

Once fixed, test these endpoints:
- `https://your-app.railway.app/health`
- `https://your-app.railway.app/docs` (API documentation)

## 🎯 Next Steps

1. **Fix Railway deployment** using one of the solutions above
2. **Get your Railway URL** (e.g., `https://your-app.railway.app`)
3. **Update Netlify** with the Railway URL:
   ```bash
   .\deploy-netlify.ps1 -BackendUrl "https://your-app.railway.app" -Production
   ```

## 💡 Pro Tips

- **Use Railway's PostgreSQL** addon for database
- **Monitor logs** during deployment
- **Test health endpoint** after deployment
- **Keep environment variables secure**

---

**🔧 This should fix your Railway deployment issue!**
