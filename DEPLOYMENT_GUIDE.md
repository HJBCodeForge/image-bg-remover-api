# 🚀 Deployment Guide - Background Remover API

## Overview
This guide will help you deploy your Background Remover API to **Render** (for the API backend) and **GitHub Pages** (for the frontend demo).

## 📋 Prerequisites
- GitHub account
- Render account (free tier available)
- Git installed locally

## 🔧 Step 1: Configure for Deployment

Run the configuration script:
```bash
./configure_deployment.sh
```

Or manually update the API URL in `demo.html`:
```javascript
const API_BASE_URL = 'https://your-app-name.onrender.com';
```

## 🌐 Step 2: Deploy API to Render

### Option A: Connect GitHub Repository (Recommended)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/bg-remover-api.git
   git push -u origin main
   ```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `bg-remover-api` (or your preferred name)
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python main.py`
     - **Instance Type**: `Free` (or paid for production)

3. **Set Environment Variables**:
   - `PORT`: `8000`
   - `SECRET_KEY`: `your-secret-key-here`
   - `DATABASE_URL`: `sqlite:///./bg_remover.db`

### Option B: Manual Upload

1. **Create a new Web Service on Render**
2. **Upload your code as a ZIP file**
3. **Follow the same configuration steps above**

## 📄 Step 3: Deploy Frontend to GitHub Pages

### Option A: Using GitHub Actions (Automatic)

1. **Push to GitHub** (if not done already):
   ```bash
   git add .
   git commit -m "Add deployment configuration"
   git push origin main
   ```

2. **Enable GitHub Pages**:
   - Go to your repository on GitHub
   - Click "Settings" → "Pages"
   - Under "Source", select "GitHub Actions"
   - The workflow will automatically deploy your site

### Option B: Manual GitHub Pages

1. **Enable GitHub Pages**:
   - Repository Settings → Pages
   - Source: "Deploy from a branch"
   - Branch: `main`
   - Folder: `/ (root)`

2. **Your site will be available at**:
   ```
   https://yourusername.github.io/repository-name
   ```

## 🔗 Step 4: Update CORS Settings

Once deployed, update the CORS settings in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourusername.github.io",
        "https://your-custom-domain.com",
        # Add your actual domains here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Step 5: Test Your Deployment

1. **Test the API**:
   ```bash
   curl https://your-app-name.onrender.com/health
   ```

2. **Test the Frontend**:
   - Visit `https://yourusername.github.io/repository-name`
   - Generate an API key
   - Upload an image and test background removal

## 🛠️ Environment Variables for Render

Set these in your Render dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `PORT` | `8000` | Server port (required by Render) |
| `SECRET_KEY` | `your-random-secret-key` | Security key for API |
| `DATABASE_URL` | `sqlite:///./bg_remover.db` | Database connection |

## 🔒 Security Considerations

1. **Change the SECRET_KEY** in production
2. **Update CORS origins** to your actual domains
3. **Use HTTPS** (automatically provided by Render)
4. **Monitor API usage** for abuse

## 📱 Custom Domain (Optional)

### For the API (Render):
- Add a custom domain in Render dashboard
- Update DNS settings with your domain provider

### For the Frontend (GitHub Pages):
- Add a `CNAME` file to your repository
- Configure DNS with your domain provider

## 🎯 URLs After Deployment

- **API**: `https://your-app-name.onrender.com`
- **API Docs**: `https://your-app-name.onrender.com/docs`
- **Frontend**: `https://yourusername.github.io/repository-name`

## 🆘 Troubleshooting

### API Issues:
- Check Render logs for errors
- Verify environment variables are set
- Ensure all dependencies are in `requirements.txt`

### Frontend Issues:
- Check browser console for CORS errors
- Verify API URL is correct in `demo.html`
- Ensure GitHub Pages is enabled

### CORS Issues:
- Update `allow_origins` in `main.py`
- Redeploy the API after changes

## 🎉 You're Live!

Once deployed, your Background Remover API will be:
- ✅ **Accessible worldwide** via HTTPS
- ✅ **Scalable** with Render's infrastructure
- ✅ **Professional** with interactive documentation
- ✅ **User-friendly** with a beautiful web interface

Your users can now:
1. Visit your GitHub Pages site
2. Generate API keys
3. Upload images and remove backgrounds
4. Integrate your API into their applications

**Congratulations! Your Background Remover API is now live! 🎊**
