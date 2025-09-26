# ⚡ Render + Netlify Quick Start Guide

## 🎯 5-Minute Deployment Checklist

### ☑️ Step 1: Deploy Backend to Render (3 minutes)

1. **Go to [render.com](https://render.com)** → Sign up with GitHub
2. **New Web Service** → Connect Law-GPT repository
3. **Configure Service**:
   ```
   Name: law-gpt-backend
   Root Directory: backend
   Runtime: Docker
   Dockerfile Path: ./Dockerfile
   ```
4. **Add Environment Variables**:
   ```
   GOOGLE_API_KEY=your_google_api_key
   INDIAN_KANOON_API_KEY=your_indian_kanoon_api_key
   SECRET_KEY=your_random_secret_key
   APP_ENV=production
   ```
5. **Create PostgreSQL Database**:
   - New PostgreSQL service
   - Copy DATABASE_URL to backend environment
6. **Deploy** → Copy your URL: `https://your-app.onrender.com`

### ☑️ Step 2: Deploy Frontend to Netlify (2 minutes)

1. **Run our deployment script**:
   ```powershell
   .\deploy-render-netlify.ps1 -RenderUrl "https://your-app.onrender.com" -Production
   ```

2. **Or manual Netlify deployment**:
   - Go to [netlify.com](https://netlify.com)
   - New site from Git → Law-GPT repository
   - Build settings:
     ```
     Build command: cd frontend && npm ci && npm run build
     Publish directory: frontend/dist
     ```
   - Environment variables:
     ```
     VITE_API_BASE_URL=https://your-app.onrender.com
     ```

## 🎉 You're Live!

- **Frontend**: `https://amazing-site-name.netlify.app`
- **Backend**: `https://your-app.onrender.com`
- **API Docs**: `https://your-app.onrender.com/docs`

## 🔧 Files Created for You

✅ **`render.yaml`** - Infrastructure as code for Render  
✅ **`RENDER_NETLIFY_DEPLOYMENT.md`** - Complete guide  
✅ **`deploy-render-netlify.ps1`** - Automated deployment  
✅ **Updated `netlify.toml`** - Configured for Render backend  
✅ **Updated `backend/Dockerfile`** - Render-optimized  

## 💡 Pro Tips

- **Start with free tiers** of both platforms
- **Render auto-deploys** on every git push
- **Netlify auto-deploys** on every git push to main
- **Both provide SSL certificates** automatically

## 🆘 Troubleshooting

### Render Issues
- Check build logs in Render dashboard
- Ensure `backend/` folder structure is correct
- Verify environment variables are set

### Netlify Issues
- Check build logs in Netlify dashboard
- Verify `frontend/dist` folder is generated
- Test API proxy with `/api/health`

### API Connection Issues
- Ensure Render URL is correct in netlify.toml
- Check CORS settings in backend
- Test direct backend URL first

## 🎯 What You Get

✅ **Full Law-GPT Application**  
✅ **Indian Kanoon API Integration**  
✅ **PostgreSQL Database**  
✅ **User Authentication**  
✅ **Document Upload & Analysis**  
✅ **AI Legal Chat**  
✅ **Mobile-Responsive UI**  
✅ **SSL/HTTPS Everywhere**  
✅ **Global CDN (Netlify)**  
✅ **Auto-scaling (Render)**  

---

**🚀 Your Law-GPT is ready for production use!**
