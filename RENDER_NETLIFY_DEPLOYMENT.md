# 🚀 Complete Deployment Guide - Render (Backend) + Netlify (Frontend)

## Your Setup:
- **Backend**: Render.com with PostgreSQL ✅
- **Frontend**: Netlify
- **Database**: PostgreSQL (External on Render) ✅ Connected!

**Your PostgreSQL URL**: 
```
postgresql://lawgpt_user:rQ1FLdtndZu9bDejYfHzm2SIyYxGKvhZ@dpg-d3bcnkvfte5s739l6lq0-a.oregon-postgres.render.com/lawgpt
```

---

## 📋 Quick Deployment Steps

### Step 1: Migrate Data to PostgreSQL (Optional)

```powershell
# Run migration script
$env:DATABASE_URL="postgresql://lawgpt_user:rQ1FLdtndZu9bDejYfHzm2SIyYxGKvhZ@dpg-d3bcnkvfte5s739l6lq0-a.oregon-postgres.render.com/lawgpt"
python scripts\migrate_sqlite_to_postgres.py $env:DATABASE_URL
```

### Step 2: Push to GitHub

```powershell
git add .
git commit -m "Deploy to production with PostgreSQL"
git push origin main
```

### Step 3: Deploy Backend to Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `law-gpt-backend`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **Add Environment Variables**:
   ```
   DATABASE_URL=postgresql://lawgpt_user:rQ1FLdtndZu9bDejYfHzm2SIyYxGKvhZ@dpg-d3bcnkvfte5s739l6lq0-a.oregon-postgres.render.com/lawgpt
   GOOGLE_API_KEY=<your_actual_api_key>
   SECRET_KEY=<generate_new_key>
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   STORAGE_DIR=/data/uploads
   APP_ENV=production
   ```

   **Generate SECRET_KEY**:
   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

6. Click **"Create Web Service"**

7. **Note your backend URL**: `https://law-gpt-backend.onrender.com`

### Step 4: Deploy Frontend to Netlify

#### Option A: Netlify CLI (Quick)

```powershell
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd frontend
netlify deploy --prod

# Follow prompts:
# - Build command: npm run build
# - Publish directory: dist
```

#### Option B: Netlify Dashboard (Easier)

1. Go to https://app.netlify.com
2. Click **"Add new site"** → **"Import an existing project"**
3. Choose **GitHub** and select your repository
4. Configure:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
   - **Build settings**: Detected as Vite ✅

5. **Environment Variables**:
   Click "Advanced" → "New variable":
   ```
   VITE_API_BASE_URL=https://law-gpt-backend.onrender.com
   ```
   (Replace with your actual Render backend URL)

6. Click **"Deploy site"**

7. **Get your Netlify URL**: `https://your-app-name.netlify.app`

### Step 5: Update Backend CORS

Edit `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://your-app-name.netlify.app",  # Your Netlify URL
        "https://*.netlify.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)
```

Push to GitHub → Render will auto-redeploy!

---

## 📁 Configuration Files

### `netlify.toml` (Already in your project!)

```toml
[build]
  base = "frontend"
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[build.environment]
  NODE_VERSION = "18"
```

### `frontend/.env.production`

Create this file:
```env
VITE_API_BASE_URL=https://law-gpt-backend.onrender.com
```

---

## 🔧 Environment Variables Summary

### Backend (Render) - Required:

```env
DATABASE_URL=postgresql://lawgpt_user:rQ1FLdtndZu9bDejYfHzm2SIyYxGKvhZ@dpg-d3bcnkvfte5s739l6lq0-a.oregon-postgres.render.com/lawgpt
GOOGLE_API_KEY=AIza...  # Your actual key
SECRET_KEY=<generate_secure_random_key>
ACCESS_TOKEN_EXPIRE_MINUTES=60
STORAGE_DIR=/data/uploads
APP_ENV=production
```

### Frontend (Netlify) - Required:

```env
VITE_API_BASE_URL=https://your-backend.onrender.com
```

---

## 🚀 Automated Deployment Script

Run this for automated deployment:

```powershell
.\deploy_to_netlify.ps1
```

Or follow manual steps above.

---

## ✅ Post-Deployment Checklist

- [ ] Backend deployed on Render
- [ ] Frontend deployed on Netlify
- [ ] Environment variables configured
- [ ] CORS updated with Netlify URL
- [ ] Health endpoint works: `https://your-backend.onrender.com/health`
- [ ] Frontend loads: `https://your-app.netlify.app`
- [ ] User registration works
- [ ] Login works
- [ ] Chat with AI works
- [ ] Document upload works

---

## 🔍 Testing Your Deployment

### 1. Test Backend Health
```
https://your-backend.onrender.com/health
```
Should return: `{"status": "ok", "timestamp": "..."}`

### 2. Test API Docs
```
https://your-backend.onrender.com/docs
```
Should show interactive API documentation

### 3. Test Frontend
1. Visit `https://your-app.netlify.app`
2. Register a new user
3. Login
4. Try the chat feature
5. Upload a document

---

## 🚨 Troubleshooting

### Backend Issues

**Build fails on Render:**
- Check `requirements.txt` is complete
- Check Python version is 3.11
- View build logs in Render dashboard

**Database connection error:**
```powershell
# Test connection locally
$env:DATABASE_URL="postgresql://..."
python -c "from backend.app.database import engine; print(engine.url)"
```

**500 errors:**
- Check Render logs for detailed errors
- Verify all environment variables are set
- Check DATABASE_URL format

### Frontend Issues

**Build fails on Netlify:**
- Check `package.json` dependencies
- Verify Node version (18+)
- Check Netlify build logs

**Cannot connect to backend:**
- Verify `VITE_API_BASE_URL` in Netlify env vars
- Check CORS settings in backend
- Open browser console for errors

**CORS errors:**
- Update `backend/app/main.py` with Netlify URL
- Push to GitHub to redeploy Render
- Clear browser cache

---

## 📞 Quick Commands

```powershell
# Migrate data
$env:DATABASE_URL="postgresql://lawgpt_user:rQ1FLdtndZu9bDejYfHzm2SIyYxGKvhZ@dpg-d3bcnkvfte5s739l6lq0-a.oregon-postgres.render.com/lawgpt"
python scripts\migrate_sqlite_to_postgres.py $env:DATABASE_URL

# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Test PostgreSQL connection
python -c "from backend.app.database import engine; print('Connected!')"

# Deploy to Netlify (CLI)
cd frontend
netlify deploy --prod

# View Render logs
# Use Render Dashboard → Logs tab

# View Netlify logs
# Use Netlify Dashboard → Deploys → [deployment] → Deploy log
```

---

## 🎉 Success!

Your Law-GPT will be live at:
- **Frontend**: https://your-app.netlify.app
- **Backend**: https://your-backend.onrender.com
- **API Docs**: https://your-backend.onrender.com/docs

**Both platforms offer free tiers and auto-deploy on git push!**

---

## 💡 Tips

### Free Tier Limitations

**Render Free:**
- Spins down after 15 minutes of inactivity
- Takes ~30 seconds to wake up
- 750 hours/month free

**Netlify Free:**
- 100 GB bandwidth/month
- 300 build minutes/month
- Auto SSL certificates

### Auto-Deploy

Both platforms auto-deploy when you push to GitHub:
- **Render**: Watches `main` branch
- **Netlify**: Watches configured branch

### Custom Domains

Both support custom domains for free:
- **Render**: Settings → Custom Domain
- **Netlify**: Domain settings → Add custom domain

---

**Need help? Check logs in Render and Netlify dashboards!**
