# 🚀 Complete Deployment Guide - Render (Backend) + Vercel (Frontend)

## Your Setup:
- **Backend**: Render.com with PostgreSQL
- **Frontend**: Vercel
- **Database**: PostgreSQL (External on Render) ✅ Connected!

**Database URL**: 
```
postgresql://lawgpt_user:rQ1FLdtndZu9bDejYfHzm2SIyYxGKvhZ@dpg-d3bcnkvfte5s739l6lq0-a.oregon-postgres.render.com/lawgpt
```

---

## 📋 Pre-Deployment Checklist

- [x] PostgreSQL database created on Render
- [x] Database connection tested ✅
- [x] Google Gemini API key obtained
- [ ] Migrate SQLite data to PostgreSQL
- [ ] Push code to GitHub
- [ ] Deploy backend to Render
- [ ] Deploy frontend to Vercel
- [ ] Update CORS settings

---

## Part 1: Migrate Your Data to PostgreSQL

### Step 1: Run Migration Script

```powershell
# Set your PostgreSQL URL
$env:DATABASE_URL="postgresql://lawgpt_user:rQ1FLdtndZu9bDejYfHzm2SIyYxGKvhZ@dpg-d3bcnkvfte5s739l6lq0-a.oregon-postgres.render.com/lawgpt"

# Run migration
.\scripts\migrate_to_postgres.ps1
```

Or manually:
```powershell
python scripts/migrate_sqlite_to_postgres.py "postgresql://lawgpt_user:rQ1FLdtndZu9bDejYfHzm2SIyYxGKvhZ@dpg-d3bcnkvfte5s739l6lq0-a.oregon-postgres.render.com/lawgpt"
```

### Step 2: Verify Migration

```powershell
# Connect to PostgreSQL
$env:DATABASE_URL="postgresql://lawgpt_user:rQ1FLdtndZu9bDejYfHzm2SIyYxGKvhZ@dpg-d3bcnkvfte5s739l6lq0-a.oregon-postgres.render.com/lawgpt"

cd backend
python -c "from app.database import SessionLocal; from app.models import User; db = SessionLocal(); print(f'Users: {db.query(User).count()}'); db.close()"
```

---

## Part 2: Deploy Backend to Render

### Option A: Using render.yaml (Recommended)

Your `render.yaml` is already configured!

1. **Push to GitHub**:
   ```powershell
   git add .
   git commit -m "Prepare for Render deployment with PostgreSQL"
   git push origin main
   ```

2. **Connect to Render**:
   - Go to https://dashboard.render.com
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Select your repository
   - Render will detect `render.yaml` automatically
   - Click "Apply"

3. **Set Environment Variables** in Render Dashboard:
   
   Go to your service → Environment tab → Add:
   
   ```
   DATABASE_URL=postgresql://lawgpt_user:rQ1FLdtndZu9bDejYfHzm2SIyYxGKvhZ@dpg-d3bcnkvfte5s739l6lq0-a.oregon-postgres.render.com/lawgpt
   
   GOOGLE_API_KEY=<your_actual_google_api_key>
   
   SECRET_KEY=<generate_new_secure_key>
   
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   
   STORAGE_DIR=/data/uploads
   
   APP_ENV=production
   ```

   **Generate SECRET_KEY**:
   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

4. **Deploy**:
   - Render will automatically build and deploy
   - Wait for deployment to complete (~5-10 minutes)
   - Note your backend URL: `https://your-app-name.onrender.com`

### Option B: Manual Deployment

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Configure:
   - **Name**: law-gpt-backend
   - **Runtime**: Docker (or Python 3.11)
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: (add all from step 3 above)

---

## Part 3: Update Backend CORS for Vercel

Update `backend/app/main.py` to allow Vercel frontend:

```python
# Update CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174", 
        "https://your-app.vercel.app",  # Add your Vercel URL here
        "https://*.vercel.app",  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Part 4: Deploy Frontend to Vercel

### Step 1: Update Frontend Configuration

Create `frontend/.env.production`:

```env
VITE_API_BASE_URL=https://your-backend-app.onrender.com
```

Update `frontend/vite.config.ts` if needed (current config is good).

### Step 2: Deploy to Vercel

#### Method 1: Vercel CLI (Recommended)

```powershell
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy from frontend directory
cd frontend
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? <your-account>
# - Link to existing project? No
# - Project name? law-gpt
# - Directory? ./
# - Override settings? No
```

#### Method 2: Vercel Dashboard

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

4. **Environment Variables**:
   ```
   VITE_API_BASE_URL=https://your-backend-app.onrender.com
   ```

5. Click "Deploy"

### Step 3: Get Your Vercel URL

After deployment, Vercel will provide a URL like:
```
https://law-gpt-xyz123.vercel.app
```

### Step 4: Update Backend CORS

Go back to your backend code and update the CORS origins with your Vercel URL, then redeploy.

---

## Part 5: Final Configuration

### 1. Update Backend CORS

Edit `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://law-gpt-xyz123.vercel.app",  # Your Vercel URL
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Push to GitHub → Render auto-deploys.

### 2. Test Your Deployment

1. Visit your Vercel frontend: `https://your-app.vercel.app`
2. Register a new user
3. Try the chat feature
4. Upload a document
5. Test all features

---

## 🔧 Environment Variables Reference

### Backend (Render)

**Required:**
```
DATABASE_URL=postgresql://lawgpt_user:rQ1FLdtndZu9bDejYfHzm2SIyYxGKvhZ@dpg-d3bcnkvfte5s739l6lq0-a.oregon-postgres.render.com/lawgpt
GOOGLE_API_KEY=<your_key>
SECRET_KEY=<generate_secure_key>
```

**Optional:**
```
ACCESS_TOKEN_EXPIRE_MINUTES=60
STORAGE_DIR=/data/uploads
APP_ENV=production
OPENAI_API_KEY=<optional>
INDIAN_KANOON_API_KEY=<optional>
```

### Frontend (Vercel)

```
VITE_API_BASE_URL=https://your-backend.onrender.com
```

---

## 📁 Files to Update Before Deployment

### 1. Update `backend/app/main.py` - CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://your-app.vercel.app",  # YOUR VERCEL URL
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Create `frontend/.env.production`

```env
VITE_API_BASE_URL=https://your-backend.onrender.com
```

### 3. Update `render.yaml` (Optional)

Already configured! Just make sure environment variables are set in Render dashboard.

---

## 🚨 Troubleshooting

### Backend Issues

**Database Connection Errors:**
```powershell
# Test connection
$env:DATABASE_URL="postgresql://..."
python -c "from backend.app.database import engine; print(engine.url)"
```

**Build Failures:**
- Check `backend/requirements.txt` is complete
- Ensure Python version matches (3.11)
- Check Render build logs

**500 Errors:**
- Check Render logs for errors
- Verify all environment variables are set
- Check DATABASE_URL format

### Frontend Issues

**Can't Connect to Backend:**
- Verify `VITE_API_BASE_URL` is correct
- Check CORS settings in backend
- Check browser console for errors

**Build Failures:**
- Check `package.json` dependencies
- Try: `npm install` locally
- Check Vercel build logs

### CORS Issues

If you see CORS errors:
1. Update backend CORS origins with Vercel URL
2. Make sure to include `https://` prefix
3. Redeploy backend after changes

---

## ✅ Deployment Checklist

### Pre-Deployment
- [x] PostgreSQL database created
- [x] Database connection tested
- [ ] Data migrated from SQLite
- [ ] Code pushed to GitHub
- [ ] Environment variables prepared

### Backend Deployment
- [ ] Render service created
- [ ] Environment variables configured
- [ ] Build successful
- [ ] Health endpoint working (`/health`)
- [ ] API docs accessible (`/docs`)

### Frontend Deployment
- [ ] Vercel project created
- [ ] Build successful
- [ ] Frontend accessible
- [ ] Can connect to backend
- [ ] Authentication working

### Final Testing
- [ ] User registration works
- [ ] Login works
- [ ] Chat with AI works
- [ ] Document upload works
- [ ] All features functional

---

## 🎉 Success!

Once deployed, your application will be live at:
- **Frontend**: https://your-app.vercel.app
- **Backend**: https://your-app.onrender.com
- **API Docs**: https://your-app.onrender.com/docs

---

## 📞 Quick Commands Reference

```powershell
# Migrate data
python scripts/migrate_sqlite_to_postgres.py "postgresql://..."

# Test PostgreSQL connection
$env:DATABASE_URL="postgresql://..."; python -c "from backend.app.database import engine; print('Connected!')"

# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Deploy to Vercel
cd frontend; vercel --prod

# Check Render logs
# Use Render Dashboard → Logs tab
```

---

**Need help? Check the logs in Render and Vercel dashboards!**
