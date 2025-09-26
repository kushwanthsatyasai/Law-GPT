# 🚀 Quick Netlify Deployment for Law-GPT

## ⚡ 5-Minute Setup

### Option 1: Frontend-Only (Quick Test)

1. **Deploy directly to Netlify**:
   ```bash
   # Build frontend
   cd frontend
   npm ci && npm run build
   
   # Deploy with drag & drop
   # Go to netlify.com → "Sites" → Drag frontend/dist folder
   ```

### Option 2: Full Production Setup

#### Step 1: Deploy Backend to Railway (3 minutes)

1. **Go to [railway.app](https://railway.app)** → Sign up
2. **Create new project** → "Deploy from GitHub repo"
3. **Select your Law-GPT repository**
4. **Set root directory**: `/backend`
5. **Add environment variables**:
   ```
   GOOGLE_API_KEY=your_key_here
   INDIAN_KANOON_API_KEY=your_key_here  
   SECRET_KEY=your_random_secret_key
   ```
6. **Deploy** → Copy the Railway URL (e.g., `https://your-app.railway.app`)

#### Step 2: Deploy Frontend to Netlify (2 minutes)

1. **Run deployment script**:
   ```powershell
   .\deploy-netlify.ps1 -BackendUrl "https://your-app.railway.app" -Production
   ```

2. **Or manual deployment**:
   - Go to [netlify.com](https://netlify.com) → "New site from Git"
   - Connect GitHub → Select Law-GPT repo
   - Build settings:
     ```
     Build command: cd frontend && npm ci && npm run build
     Publish directory: frontend/dist
     ```
   - Environment variables:
     ```
     VITE_API_BASE_URL=https://your-app.railway.app
     ```

## 🎯 Live in 5 Minutes!

Your Law-GPT application will be live at:
- **Frontend**: `https://your-site.netlify.app`
- **Backend**: `https://your-app.railway.app`

## 🔧 Alternative Quick Options

### Option A: Render + Netlify
- **Backend**: Deploy to [render.com](https://render.com) (free tier)
- **Frontend**: Deploy to Netlify

### Option B: Vercel Full-Stack
- **Everything**: Deploy to [vercel.com](https://vercel.com)

### Option C: Railway Full-Stack
- **Everything**: Deploy to [railway.app](https://railway.app)

## 📱 Features After Deployment

✅ **Indian Legal Search** with real API  
✅ **Document Analysis** and upload  
✅ **AI Chat Assistant**  
✅ **User Authentication**  
✅ **Real-time responses**  
✅ **Mobile-responsive UI**  

## 🔑 API Keys You Need

1. **Google Gemini API** (Required)
   - Get from: https://aistudio.google.com/app/apikey
   - Free tier: 15 requests/minute

2. **Indian Kanoon API** (Required for real data)
   - Get from: https://api.indiankanoon.org/pricing/
   - Cost: ₹0.50 per search
   - Free ₹500 credit on signup

## 💡 Pro Tips

- **Start with mock data** (no API keys needed)
- **Add real API keys later** for production
- **Use Railway's free tier** for backend
- **Netlify's free tier** is perfect for frontend

## 🆘 Need Help?

1. **Check logs** in Railway/Netlify dashboards
2. **Test health endpoint**: `your-backend-url/health`
3. **View deployment guide**: [NETLIFY_DEPLOYMENT.md](NETLIFY_DEPLOYMENT.md)

---

**🎉 Your Law-GPT is ready for the world!**
