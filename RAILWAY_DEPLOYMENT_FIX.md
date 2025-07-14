# Railway Deployment Fix

## Problem
Getting error: `ERROR: failed to build: failed to solve: the Dockerfile cannot be empty`

## Solution Applied

### 1. Created Proper Dockerfile
- Added system dependencies for OpenCV/image processing
- Simplified configuration for Railway compatibility
- Uses `$PORT` environment variable from Railway

### 2. Updated railway.json
- Removed explicit builder configuration
- Let Railway auto-detect build method
- Simplified deployment configuration

### 3. Alternative Deployment Methods

#### Option A: Docker Deployment (Current)
Railway will use the Dockerfile automatically.

#### Option B: Nixpacks (Alternative)
If Docker fails, delete the Dockerfile and Railway will use Nixpacks:
```bash
rm Dockerfile
git commit -am "Remove Dockerfile for Nixpacks"
git push
```

#### Option C: Manual Configuration
In Railway dashboard:
1. Go to Settings → Environment
2. Add these variables:
   - `PORT`: (Railway sets this automatically)
   - `PYTHONPATH`: `/app`
   - `ENVIRONMENT`: `production`

### 4. Deployment Steps

1. **Commit the fixes:**
   ```bash
   git add -A
   git commit -m "Add Railway Dockerfile and configuration"
   git push
   ```

2. **Deploy on Railway:**
   - Go to your Railway project
   - Click "Deploy" or it should auto-deploy from GitHub
   - Wait for build to complete (~2-5 minutes)

3. **Monitor deployment:**
   - Check build logs in Railway dashboard
   - Look for any errors in the deployment tab

### 5. Testing Deployment

Once deployed, test these endpoints:
- `https://your-app.railway.app/` - Root endpoint
- `https://your-app.railway.app/health` - Health check
- `https://your-app.railway.app/docs` - API documentation

### 6. Common Issues & Solutions

#### Issue: Build still fails
**Solution:** Delete Dockerfile and let Railway use Nixpacks:
```bash
rm Dockerfile
git commit -am "Use Nixpacks instead of Docker"
git push
```

#### Issue: App crashes on startup
**Solution:** Check if all dependencies are in requirements.txt:
```bash
pip freeze > requirements.txt
git commit -am "Update requirements.txt"
git push
```

#### Issue: Port binding error
**Solution:** Railway automatically sets PORT. The Dockerfile now uses `$PORT`.

#### Issue: Memory issues
**Solution:** Railway has 8GB RAM, so this shouldn't be an issue anymore!

### 7. Update Frontend URLs

Once deployed successfully, update your frontend:
```bash
./update_api_urls.sh https://your-app-name.railway.app
git commit -am "Update API URLs for Railway"
git push
```

### 8. Expected Results

✅ **No more memory errors** (8GB vs 512MB)
✅ **Faster startup** (no cold starts)
✅ **Better performance** (8 vCPU vs 1 vCPU)
✅ **Reliable service** (no random shutdowns)

## Update: Fixed PORT Environment Variable Issue

### Problem
Getting error: `Error: Invalid value for '--port': '$PORT' is not a valid integer.`

### Root Cause
The Dockerfile was trying to use `$PORT` directly in the CMD instruction, but environment variables aren't expanded in exec form CMD.

### Solution Applied
1. **Created startup script** (`start.sh`) that properly handles environment variables
2. **Updated Dockerfile** to use the startup script instead of direct uvicorn command
3. **Updated railway.json** to use the startup script
4. **Updated Procfile** for consistency

### Files Modified
- `start.sh` - New startup script with proper PORT handling
- `Dockerfile` - Updated to use startup script
- `railway.json` - Updated start command
- `Procfile` - Updated for consistency

### How it works
```bash
# start.sh handles the PORT variable properly
PORT=${PORT:-8000}
exec uvicorn main:app --host 0.0.0.0 --port $PORT
```

This ensures Railway's PORT environment variable is correctly passed to uvicorn.

## Files Modified
- `Dockerfile` - Created Railway-compatible Docker configuration
- `railway.json` - Simplified Railway configuration
- This troubleshooting guide

## Next Steps
1. Commit and push these changes
2. Wait for Railway deployment
3. Test the API endpoints
4. Update frontend URLs
5. Celebrate working ML API! 🎉
