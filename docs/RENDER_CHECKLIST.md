# ✅ Render Deployment Checklist

## Pre-Deployment (Done ✓)

- [x] Updated `requirements.txt` with compatible versions
- [x] Created `runtime.txt` (Python 3.11.0)
- [x] Created `render.yaml` configuration
- [x] Created `pip.conf` for binary packages
- [x] Added `.gitignore` to protect `.env`
- [x] Created `.env.example` template
- [x] CORS is configured in `main.py`

## Render Dashboard Setup

### 1. Create Web Service
- [ ] Go to https://dashboard.render.com/
- [ ] Click "New +" → "Web Service"
- [ ] Connect GitHub repo: `Snuc-Potential-Robotics/Potential-Club`
- [ ] Select branch: `heisenberg-lab`

### 2. Basic Configuration
```
Name: potential-club-backend
Region: Oregon (US West)
Branch: heisenberg-lab
Root Directory: backend
Runtime: Python 3
Python Version: 3.11.0
```

### 3. Build Configuration

**Build Command:**
```bash
python --version && pip install --upgrade pip setuptools wheel && pip install --only-binary=:all: --no-cache-dir -r requirements.txt || pip install --no-cache-dir -r requirements.txt
```

**Start Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 4. Environment Variables (CRITICAL!)
Add these in Render Dashboard → Environment:

```
PYTHON_VERSION=3.11.0
SUPABASE_URL=https://wtkkltoieqjahzkqhnud.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind0a2tsdG9pZXFqYWh6a3FobnVkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY1Nzg1OTMsImV4cCI6MjA3MjE1NDU5M30.NBdXXSEbr77EjdVdXO6sG8_P45wESIvkt42ck7mMi8o
GOOGLE_API_KEY=AIzaSyBqeA93brrTqM9bvjGy3TqTOYQcRpsfjT4
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

⚠️ **IMPORTANT:** Update `CORS_ORIGINS` with your actual frontend URL once deployed!

### 5. Deploy!
- [ ] Click "Create Web Service"
- [ ] Wait for build to complete (3-5 minutes)
- [ ] Check logs for any errors
- [ ] Copy your Render URL (e.g., `https://potential-club-backend.onrender.com`)

## Post-Deployment

### 6. Test Your API
```bash
# Replace with your actual Render URL
curl https://YOUR-APP.onrender.com/
```

Expected response: Your API response or health check

### 7. Update Frontend
Update your frontend `.env` file:
```env
VITE_API_URL=https://YOUR-APP.onrender.com
```

### 8. Update CORS
In Render Dashboard → Environment → Add your frontend URL:
```
CORS_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app
```

### 9. Monitor
- [ ] Check Render Dashboard → Logs
- [ ] Verify all endpoints work
- [ ] Test WebSocket connections
- [ ] Monitor response times

## Troubleshooting

### Build Fails with Rust Error
✅ **Fixed!** The updated `requirements.txt` uses pre-built wheels.

### Wrong Python Version
- Check `runtime.txt` says `python-3.11.0`
- Check environment variable `PYTHON_VERSION=3.11.0`
- Clear Render build cache and redeploy

### CORS Issues
- Add your frontend domain to `CORS_ORIGINS` in Render env vars
- Format: `http://localhost:5173,https://yourdomain.com` (comma-separated, no spaces)

### App Sleeps (Free Tier)
- Free tier sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds
- Upgrade to paid tier for always-on service

### Environment Variables Not Loading
- Ensure all variables are added in Render Dashboard
- Restart the service after adding new variables
- Check logs for `Settings` validation errors

## Success Criteria ✨

- [ ] Build completes without errors
- [ ] Service shows "Live" status in Render
- [ ] API responds to `curl https://your-url.onrender.com/`
- [ ] Frontend can connect to backend
- [ ] WebSocket connections work
- [ ] No CORS errors in browser console

## Next Steps

1. **Custom Domain** (Optional)
   - Render Settings → Custom Domains
   - Add your domain and configure DNS

2. **Health Checks**
   - Add `/health` endpoint to your FastAPI app
   - Configure in Render Settings → Health Check Path

3. **Monitoring**
   - Set up error tracking (Sentry, etc.)
   - Monitor logs regularly
   - Set up alerts for downtime

4. **Scaling**
   - Upgrade to paid plan for better performance
   - Enable auto-scaling if needed
   - Consider Redis for caching

---

## 🎉 You're Ready!

Just push your changes to GitHub and follow the Render setup steps above.

**Need help?** Check `RENDER_DEPLOYMENT.md` for detailed instructions.
