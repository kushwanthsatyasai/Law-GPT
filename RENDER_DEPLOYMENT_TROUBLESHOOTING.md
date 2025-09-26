# 🔧 Render Deployment Troubleshooting Guide

## 🔥 Fixed: psycopg2 ModuleNotFoundError

### The Problem
```
ModuleNotFoundError: No module named 'psycopg2'
```

### The Solution ✅
Updated `backend/app/database.py` to use **psycopg3** instead of psycopg2:

```python
# OLD (causing error)
DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"

# NEW (fixed)
DATABASE_URL = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"
```

### What Changed
1. **Database URL format**: Added `+psycopg` to specify psycopg3 driver
2. **Automatic URL conversion**: Handles different PostgreSQL URL formats
3. **Fallback mechanism**: Falls back to SQLite if PostgreSQL fails
4. **Connection testing**: Tests database connection on startup

## 🚀 Redeploy Instructions

### Option 1: Automatic Redeploy
Push your changes to GitHub - Render will auto-deploy:
```bash
git add .
git commit -m "Fix psycopg2 database connection error"
git push origin main
```

### Option 2: Manual Redeploy
1. Go to your **Render dashboard**
2. Select your **law-gpt-backend** service
3. Click **Manual Deploy** → **Deploy latest commit**

## 🔍 Verify the Fix

### 1. Check Render Logs
In your Render dashboard, check the logs for:
```
✅ Database connected successfully: postgresql+psycopg://***
```

### 2. Test Health Endpoint
```bash
curl https://your-app.onrender.com/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 3. Test Detailed Health Check
```bash
curl https://your-app.onrender.com/health/detailed
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00Z",
  "database": "healthy",
  "api_keys": {
    "google_api_key": true,
    "indian_kanoon_api_key": true
  }
}
```

## 🗄️ Database Configuration

### Render PostgreSQL
Render automatically provides `DATABASE_URL` when you add a PostgreSQL service:
```
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

The app will automatically convert this to:
```
postgresql+psycopg://user:pass@host:port/dbname
```

### Environment Variables in Render
Make sure these are set in your Render service:

**Required:**
```
GOOGLE_API_KEY=your_google_api_key
INDIAN_KANOON_API_KEY=your_indian_kanoon_api_key
SECRET_KEY=your_secret_key
```

**Automatically provided by Render:**
```
DATABASE_URL=postgresql://...  # From PostgreSQL service
PORT=10000  # Or whatever port Render assigns
```

## ⚡ Performance Optimizations

### Single Worker Start
The Dockerfile now starts with 1 worker for stability:
```dockerfile
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
```

### Scale Up Later
Once stable, you can increase workers in Render dashboard:
- **Environment Variables** → Add `UVICORN_WORKERS=2`
- Or update Dockerfile: `--workers 2`

## 🚨 Common Issues After Fix

### 1. Database Connection Timeout
```
database connection failed: timeout
```
**Solution**: Render PostgreSQL might be starting up. Wait 2-3 minutes.

### 2. Missing Environment Variables
```
api_keys: { "google_api_key": false }
```
**Solution**: Check Render dashboard → Environment → Add missing API keys.

### 3. Application Still Crashing
**Check logs for**:
- Import errors
- Missing dependencies
- Configuration issues

### 4. Health Check Fails
```bash
# Test individual components
curl https://your-app.onrender.com/health  # Basic health
curl https://your-app.onrender.com/docs    # API documentation
```

## 🎯 Next Steps After Fix

1. **✅ Verify backend is healthy**
2. **🌐 Deploy frontend to Netlify**:
   ```powershell
   .\deploy-render-netlify.ps1 -RenderUrl "https://your-app.onrender.com" -Production
   ```
3. **🔗 Test end-to-end functionality**
4. **📊 Monitor performance**

## 💡 Pro Tips

- **Monitor Render logs** during deployment
- **Use SQLite fallback** for local development
- **Test health endpoints** first
- **Add API keys gradually** to identify issues
- **Start with 1 worker** then scale up

## 🆘 Still Having Issues?

### Debug Steps
1. **Check Render service logs**
2. **Verify environment variables**
3. **Test database connection separately**
4. **Try SQLite mode locally**: Remove `DATABASE_URL` env var

### Contact Support
- **Render Support**: help.render.com
- **Check our troubleshooting**: RENDER_NETLIFY_DEPLOYMENT.md

---

**🎉 Your psycopg2 error is now fixed! Redeploy and your backend should work perfectly.**
