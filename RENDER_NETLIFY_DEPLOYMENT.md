# 🚀 Render + Netlify Deployment Guide for Law-GPT

## 🎯 Perfect Combination
- **Backend**: Render (Excellent Python support, Free PostgreSQL)
- **Frontend**: Netlify (Lightning fast CDN, Easy React deployment)

## 🔧 Step 1: Deploy Backend to Render

### Option A: Web Dashboard (Recommended)

1. **Go to [render.com](https://render.com)** and sign up
2. **Connect GitHub**: Link your Law-GPT repository
3. **Create Web Service**:
   - **Name**: `law-gpt-backend`
   - **Repository**: Your Law-GPT repo
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Docker`
   - **Dockerfile Path**: `./Dockerfile`

### Option B: Using render.yaml (Infrastructure as Code)

The `render.yaml` file I created will automatically set up everything:

```yaml
services:
  - type: web
    name: law-gpt-backend
    runtime: docker
    dockerfilePath: ./backend/Dockerfile
    dockerContext: ./backend
    plan: free
    healthCheckPath: /health
```

## 🔑 Step 2: Configure Environment Variables in Render

Go to your Render service → **Environment** → Add these:

```env
# Required API Keys
GOOGLE_API_KEY=your_google_gemini_api_key
INDIAN_KANOON_API_KEY=your_indian_kanoon_api_key
SECRET_KEY=your_super_secret_key_change_this

# Database (Render will provide this automatically)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Optional API Keys
OPENAI_API_KEY=your_openai_key
SCC_ONLINE_API_KEY=your_scc_online_key
KANOON_DEV_API_KEY=your_kanoon_dev_key

# App Configuration
APP_ENV=production
STORAGE_DIR=/data/uploads
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## 🗄️ Step 3: Add PostgreSQL Database

1. **In Render Dashboard**: Create new **PostgreSQL** service
2. **Name**: `law-gpt-database`
3. **Plan**: Free (256MB RAM, 1GB storage)
4. **Copy Database URL**: Render provides the connection string
5. **Add to Backend**: Set `DATABASE_URL` environment variable

## 🌐 Step 4: Deploy Frontend to Netlify

### Quick Deploy Method

1. **Update netlify.toml** with your Render URL:
   ```toml
   [[redirects]]
     from = "/api/*"
     to = "https://YOUR-BACKEND-URL.onrender.com/:splat"
   ```

2. **Deploy using our script**:
   ```powershell
   .\deploy-netlify.ps1 -BackendUrl "https://YOUR-BACKEND-URL.onrender.com" -Production
   ```

### Manual Netlify Setup

1. **Go to [netlify.com](https://netlify.com)**
2. **New site from Git** → Connect GitHub → Select Law-GPT
3. **Build Settings**:
   ```
   Build command: cd frontend && npm ci && npm run build
   Publish directory: frontend/dist
   Base directory: (leave empty)
   ```
4. **Environment Variables**:
   ```
   VITE_API_BASE_URL=https://YOUR-BACKEND-URL.onrender.com
   NODE_VERSION=20
   ```

## 🔄 Complete Deployment Process

### Step-by-Step Walkthrough

1. **Deploy Backend to Render**:
   ```bash
   # Push your code to GitHub first
   git add .
   git commit -m "Configure for Render deployment"
   git push origin main
   ```

2. **Get your Render URL**: 
   - After deployment: `https://law-gpt-backend.onrender.com`

3. **Test Backend**:
   ```bash
   curl https://law-gpt-backend.onrender.com/health
   ```

4. **Deploy Frontend to Netlify**:
   ```powershell
   # Update with your actual Render URL
   .\deploy-netlify.ps1 -BackendUrl "https://law-gpt-backend.onrender.com" -Production
   ```

5. **Test Full Application**:
   - Frontend: `https://your-site.netlify.app`
   - API working through proxy

## 📊 Service Comparison

| Feature | Render | Netlify |
|---------|--------|---------|
| **Backend Support** | ✅ Excellent Python | ❌ Functions only |
| **Database** | ✅ Free PostgreSQL | ❌ No database |
| **Docker Support** | ✅ Full support | ❌ No |
| **Static Hosting** | ⚠️ Basic | ✅ Excellent CDN |
| **Build Speed** | ⚠️ Slower | ✅ Very fast |
| **Free Tier** | ✅ 750 hours/month | ✅ 100GB bandwidth |

## 💰 Cost Breakdown

### Free Tier Limits
- **Render**: 750 hours/month, 512MB RAM, Free PostgreSQL
- **Netlify**: 100GB bandwidth, 300 build minutes

### Paid Plans (if needed)
- **Render**: $7/month (Starter plan)
- **Netlify**: $19/month (Pro plan)

## 🔧 Configuration Files Created

✅ **`render.yaml`** - Render infrastructure configuration  
✅ **Updated `netlify.toml`** - Points to Render backend  
✅ **Updated `backend/Dockerfile`** - Render-optimized  
✅ **Environment configurations** - For both platforms  

## 🚀 Deployment Scripts

### For Render Backend
```bash
# Automatic via GitHub integration
git push origin main
# Render auto-deploys on push
```

### For Netlify Frontend
```powershell
# Use our automated script
.\deploy-netlify.ps1 -BackendUrl "https://your-backend.onrender.com" -Production
```

## 🔍 Testing Your Deployment

### Backend Health Check
```bash
curl https://your-backend.onrender.com/health
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

### Frontend API Test
```bash
curl https://your-site.netlify.app/api/health
# Should proxy to Render backend
```

## 🌍 Custom Domain Setup

### For Render (Backend)
1. **Render Dashboard** → Service → Settings
2. **Custom Domain** → Add your API domain
3. **SSL**: Automatically provided

### For Netlify (Frontend)
1. **Netlify Dashboard** → Site → Domain settings
2. **Add custom domain**
3. **SSL**: Automatically provided

## 🔧 Troubleshooting

### Common Issues

1. **Render deployment fails**:
   ```bash
   # Check build logs in Render dashboard
   # Ensure Dockerfile is in backend/ folder
   ```

2. **Netlify can't reach backend**:
   ```bash
   # Check CORS settings
   # Verify Render URL in netlify.toml
   ```

3. **Database connection errors**:
   ```bash
   # Check DATABASE_URL in Render environment
   # Ensure PostgreSQL service is running
   ```

### Performance Tips

1. **Render**: Use persistent disk for file uploads
2. **Netlify**: Enable asset optimization
3. **Both**: Monitor usage and upgrade if needed

## 🎯 Advantages of This Setup

✅ **Render Benefits**:
- Better Python/Docker support than Railway
- Free PostgreSQL database
- Automatic SSL certificates
- Easy environment variable management

✅ **Netlify Benefits**:
- Lightning-fast global CDN
- Excellent React/Vite support
- Advanced deployment features
- Great developer experience

✅ **Combined Benefits**:
- Clear separation of concerns
- Independent scaling
- Best tool for each job
- Cost-effective

## 📈 Monitoring and Maintenance

### Render Monitoring
- **Logs**: Available in dashboard
- **Metrics**: CPU, Memory, Response time
- **Alerts**: Email notifications

### Netlify Monitoring
- **Analytics**: Built-in website analytics
- **Function logs**: For any edge functions
- **Performance**: Lighthouse integration

## 🎉 Final Steps

1. **Deploy backend to Render** ✅
2. **Deploy frontend to Netlify** ✅  
3. **Test all functionality** ✅
4. **Set up custom domains** (optional)
5. **Monitor and optimize** 📊

---

**🌟 Your Law-GPT application will be live with the best hosting for each component!**
