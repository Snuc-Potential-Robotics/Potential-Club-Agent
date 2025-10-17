# 🚀 Render Deployment Guide - Potential Club Backend

## Quick Fix for Build Errors

The build errors you're seeing are caused by:
- Python 3.13 lacking pre-built wheels for older packages
- Rust compilation failing due to read-only filesystem

## ✅ Solution Applied

### 1. Updated Dependencies (`requirements.txt`)
- Upgraded Pydantic to 2.6.4 (has Python 3.11 wheels)
- Pinned all dependencies to versions with pre-built wheels
- No Rust/C compilation required

### 2. Configured Build Settings
- Forces Python 3.11.0 (stable, well-supported)
- Uses `--only-binary` flag to prevent source builds
- Fallback command if binary-only fails

### 3. Created Helper Files
- `runtime.txt`: Specifies Python 3.11.0
- `pip.conf`: Forces binary package installation
- `render.yaml`: Complete Render configuration

## 🛠️ Render Dashboard Setup

### Step 1: Create Web Service
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `Snuc-Potential-Robotics/Potential-Club`

### Step 2: Configure Service
```
Name: potential-club-backend
Region: Oregon (US West)
Branch: heisenberg-lab (or main)
Root Directory: backend
Runtime: Python 3
```

### Step 3: Build & Start Commands
**Build Command:**
```bash
python --version && pip install --upgrade pip setuptools wheel && pip install --only-binary=:all: --no-cache-dir -r requirements.txt || pip install --no-cache-dir -r requirements.txt
```

**Start Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 4

```

### Step 4: Environment Variables
Add these in Render Dashboard under "Environment":

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.0` |
| `SUPABASE_URL` | `https://wtkkltoieqjahzkqhnud.supabase.co` |
| `SUPABASE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `GOOGLE_API_KEY` | `AIzaSyBqeA93brrTqM9bvjGy3TqTOYQcRpsfjT4` |
| `ENVIRONMENT` | `production` |

**⚠️ IMPORTANT:** Never commit the `.env` file to Git! Use Render's environment variables instead.

### Step 5: Advanced Settings
- **Auto-Deploy**: Yes (recommended)
- **Health Check Path**: `/` or `/health` (if you have a health endpoint)
- **Plan**: Free (for testing) or Starter (for production)

## 🔍 Troubleshooting

### If Build Still Fails

**Option A: Use render.yaml (Recommended)**
1. Ensure `render.yaml` is in the `backend` folder
2. In Render: Settings → "Build Filter" → Leave empty
3. Render will auto-detect and use `render.yaml`

**Option B: Manual Configuration**
If `render.yaml` doesn't work, manually set in Render Dashboard:

**Environment Variables:**
```
PYTHON_VERSION=3.11.0
PIP_NO_BUILD_ISOLATION=false
```

**Build Command:**
```bash
pip install --upgrade pip setuptools wheel && pip install --prefer-binary --no-cache-dir -r requirements.txt
```

### If Pydantic Still Fails
Try this alternative `requirements.txt` (more conservative versions):
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.3
pydantic-settings==2.1.0
langchain==0.1.0
langchain-google-genai==0.0.6
langgraph==0.0.20
supabase==2.3.0
python-dotenv==1.0.0
websockets==12.0
httpx==0.25.2
```

## 📝 Verify Deployment

Once deployed, test your API:
```bash
# Get your Render URL (e.g., https://potential-club-backend.onrender.com)
curl https://YOUR-RENDER-URL.onrender.com/

# Test with your frontend
# Update VITE_API_URL in your frontend .env:
VITE_API_URL=https://YOUR-RENDER-URL.onrender.com
```

## 🎯 Next Steps After Deployment

1. **Enable CORS** in `main.py` for your frontend domain
2. **Add Health Check Endpoint** (prevents cold starts)
3. **Monitor Logs** in Render Dashboard
4. **Set up Custom Domain** (optional)
5. **Enable Auto-Deploy** from GitHub

## 💡 Pro Tips

- **Cold Starts**: Free tier sleeps after 15 min inactivity
- **Logs**: View real-time in Render Dashboard → Logs
- **Secrets**: Never commit API keys - use Render env vars
- **Database**: Your Supabase is already configured
- **Updates**: Push to GitHub → Render auto-deploys

## 🆘 Still Having Issues?

Check Render logs for specific errors:
```bash
# In Render Dashboard → Your Service → Logs
# Look for Python version and package installation logs
```

Common issues:
- ❌ Wrong Python version → Check `runtime.txt`
- ❌ Missing env vars → Add in Render Dashboard
- ❌ Build timeout → Reduce dependencies or upgrade plan
- ❌ Port issues → Render provides `$PORT` automatically

---

**Ready to Deploy!** 🚀
Just push these changes and Render should build successfully!
