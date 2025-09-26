# 🌐 Netlify Deployment Guide for Law-GPT

## Overview

Law-GPT can be deployed to Netlify using two approaches:

1. **🚀 Hybrid Deployment (Recommended)**: Frontend on Netlify + Backend on Railway/Render
2. **⚡ Serverless Deployment**: Frontend + Basic API functions on Netlify

## 🎯 Option 1: Hybrid Deployment (Recommended)

This approach provides the best performance and feature completeness.

### Step 1: Deploy Backend to Railway

1. **Create Railway Account**: Visit [railway.app](https://railway.app)
2. **Deploy Backend**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   
   # Create new project
   railway new
   
   # Deploy backend
   cd backend
   railway up
   ```

3. **Configure Environment Variables in Railway**:
   ```env
   GOOGLE_API_KEY=your_google_api_key
   INDIAN_KANOON_API_KEY=your_indian_kanoon_api_key
   SECRET_KEY=your_secret_key
   DATABASE_URL=postgresql://...  # Railway provides this
   ```

4. **Get Railway Backend URL**: Copy your Railway app URL (e.g., `https://your-app.railway.app`)

### Step 2: Deploy Frontend to Netlify

1. **Connect Repository**:
   - Go to [netlify.com](https://netlify.com)
   - Click "New site from Git"
   - Connect your GitHub repository
   - Select Law-GPT repository

2. **Configure Build Settings**:
   ```
   Build command: cd frontend && npm ci && npm run build
   Publish directory: frontend/dist
   ```

3. **Set Environment Variables in Netlify**:
   ```env
   VITE_API_BASE_URL=https://your-app.railway.app
   VITE_APP_ENV=production
   NODE_VERSION=20
   ```

4. **Update netlify.toml**:
   ```toml
   [[redirects]]
     from = "/api/*"
     to = "https://your-app.railway.app/:splat"
     status = 200
     force = true
   ```

## ⚡ Option 2: Serverless Deployment

Use Netlify Functions for basic API functionality.

### Setup Steps

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Configure Environment Variables in Netlify**:
   ```env
   GOOGLE_API_KEY=your_google_api_key
   INDIAN_KANOON_API_KEY=your_indian_kanoon_api_key
   NODE_VERSION=20
   ```

3. **Deploy to Netlify**:
   ```bash
   # Using Netlify CLI
   npm install -g netlify-cli
   netlify login
   netlify init
   netlify deploy --prod
   ```

## 🔧 Configuration Files

### netlify.toml
```toml
[build]
  publish = "frontend/dist"
  command = "cd frontend && npm ci && npm run build"
  functions = "netlify/functions"

[build.environment]
  NODE_VERSION = "20"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Frontend Environment
```typescript
// frontend/src/config/api.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.PROD ? window.location.origin : 'http://localhost:8000');
```

## 🚀 Deployment Process

### Method 1: GitHub Integration (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Configure for Netlify deployment"
   git push origin main
   ```

2. **Auto-Deploy**: Netlify will automatically build and deploy on every push

### Method 2: Manual Deployment

1. **Build Locally**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy**:
   ```bash
   netlify deploy --dir=frontend/dist --prod
   ```

## 🔑 API Keys and Security

### Required Environment Variables

For **Hybrid Deployment**:
- Railway: `GOOGLE_API_KEY`, `INDIAN_KANOON_API_KEY`, `SECRET_KEY`
- Netlify: `VITE_API_BASE_URL`

For **Serverless Deployment**:
- Netlify: `GOOGLE_API_KEY`, `INDIAN_KANOON_API_KEY`

### Security Best Practices

1. **Never expose API keys in frontend code**
2. **Use environment variables for all secrets**
3. **Enable HTTPS (automatic on Netlify)**
4. **Configure CORS properly**

## 🌍 Custom Domain Setup

1. **Add Domain in Netlify**:
   - Go to Site settings → Domain management
   - Add custom domain

2. **Configure DNS**:
   ```
   CNAME    www    your-site.netlify.app
   A        @      75.2.60.5
   ```

3. **SSL Certificate**: Automatically provided by Netlify

## 📊 Features Available by Deployment Type

| Feature | Hybrid | Serverless |
|---------|--------|------------|
| Frontend | ✅ Full | ✅ Full |
| User Auth | ✅ Full | ❌ Limited |
| Document Upload | ✅ Full | ❌ No |
| Legal Search | ✅ Full | ✅ Basic |
| Indian Kanoon API | ✅ Full | ✅ Yes |
| Database | ✅ PostgreSQL | ❌ No |
| File Storage | ✅ Yes | ❌ No |

## 🔧 Troubleshooting

### Common Issues

1. **Build Fails**:
   ```bash
   # Check Node version
   NODE_VERSION=20  # Set in Netlify
   
   # Clear cache
   netlify build --clear-cache
   ```

2. **API Calls Fail**:
   ```javascript
   // Check CORS and proxy settings
   // Verify environment variables
   console.log(import.meta.env.VITE_API_BASE_URL);
   ```

3. **Functions Error**:
   ```bash
   # Test functions locally
   netlify dev
   ```

### Performance Optimization

1. **Enable Build Plugins**:
   ```toml
   [[plugins]]
     package = "@netlify/plugin-lighthouse"
   
   [[plugins]]
     package = "netlify-plugin-minify-html"
   ```

2. **Optimize Assets**:
   ```javascript
   // vite.config.ts
   build: {
     rollupOptions: {
       output: {
         manualChunks: {
           vendor: ['react', 'react-dom']
         }
       }
     }
   }
   ```

## 📈 Monitoring and Analytics

1. **Netlify Analytics**: Enable in site dashboard
2. **Function Logs**: View in Netlify dashboard
3. **Performance**: Use Lighthouse plugin

## 💰 Cost Estimation

### Netlify (Free Tier)
- 100GB bandwidth/month
- 300 build minutes/month
- 125,000 function invocations/month

### Railway (Hobby Plan)
- $5/month
- 500MB RAM
- 1GB disk space

## 🎯 Next Steps

1. Choose your deployment strategy
2. Set up backend (if using hybrid)
3. Configure environment variables
4. Deploy and test
5. Set up custom domain
6. Monitor and optimize

---

**🎉 Your Law-GPT application will be live on Netlify with full Indian Kanoon API integration!**
