# Complete Render.com Deployment Guide

This guide will help you deploy both the backend API and frontend to Render.com.

## 🚀 Option 1: Deploy Backend and Frontend Separately (Recommended)

### Step 1: Deploy Backend API

1. **Sign up for Render.com**
   - Go to [render.com](https://render.com) and create an account
   - Connect your GitHub account

2. **Create a New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your `bg-remover-api` repository

3. **Configure Backend Service**
   - **Name**: `bg-remover-api` (or your preferred name)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: Select "Free" (or upgrade as needed)

4. **Set Environment Variables**
   - In the service settings, go to "Environment"
   - Add these variables:
     ```
     PORT=10000
     HOST=0.0.0.0
     ENVIRONMENT=production
     ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete (5-10 minutes)
   - Note your API URL: `https://your-service-name.onrender.com`

### Step 2: Deploy Frontend

1. **Create Another Web Service**
   - Click "New +" → "Static Site"
   - Connect the same GitHub repository

2. **Configure Frontend Service**
   - **Name**: `bg-remover-frontend` (or your preferred name)
   - **Build Command**: `echo "No build required"`
   - **Publish Directory**: `.` (root directory)

3. **Deploy Frontend**
   - Click "Create Static Site"
   - Wait for deployment to complete
   - Note your frontend URL: `https://your-frontend-name.onrender.com`

### Step 3: Update API URLs

1. **Update demo.html**
   - Replace the API_BASE_URL with your backend URL:
   ```javascript
   const API_BASE_URL = 'https://your-service-name.onrender.com';
   ```

2. **Update index.html**
   - Replace the API_BASE_URL with your backend URL

3. **Commit and Push Changes**
   ```bash
   git add .
   git commit -m "Update API URLs for Render deployment"
   git push origin main
   ```

## 🔧 Option 2: Use Blueprint (Single Repository)

If you prefer to deploy from a single repository with both services:

1. **Create a Blueprint**
   - Go to Render Dashboard
   - Click "New +" → "Blueprint"
   - Connect your repository
   - Render will automatically detect the `render.yaml` file

2. **Review Configuration**
   - The blueprint will create both services automatically
   - Backend: Web service with Python runtime
   - Frontend: Static site service

3. **Deploy**
   - Click "Apply" to deploy both services
   - Wait for both deployments to complete

## 📋 Pre-Deployment Checklist

- [ ] Repository is pushed to GitHub
- [ ] `requirements.txt` is complete and accurate
- [ ] `render.yaml` is properly configured
- [ ] Environment variables are set
- [ ] CORS origins include your Render domains

## 🌐 After Deployment

### Backend Service
- API will be available at: `https://your-api-name.onrender.com`
- Test endpoints:
  - `GET /` - API information
  - `POST /api-keys` - Generate API key
  - `POST /remove-background` - Remove background

### Frontend Service
- Frontend will be available at: `https://your-frontend-name.onrender.com`
- Test functionality:
  - Landing page loads
  - Demo page works
  - API key generation works
  - Background removal works

## 🔍 Testing Your Deployment

1. **Test API Directly**
   ```bash
   curl https://your-api-name.onrender.com/
   ```

2. **Test Frontend**
   - Visit your frontend URL
   - Try generating an API key
   - Upload an image and remove background

3. **Test CORS**
   - Make sure frontend can communicate with backend
   - Check browser console for CORS errors

## 🚨 Troubleshooting

### Common Issues

1. **Build Fails**
   - Check build logs in Render dashboard
   - Verify `requirements.txt` is correct
   - Ensure Python version compatibility

2. **Service Won't Start**
   - Check service logs
   - Verify `PORT` environment variable is set
   - Ensure start command is correct

3. **CORS Errors**
   - Update CORS origins in `main.py`
   - Add your Render domains to allowed origins

4. **API Key Generation Fails**
   - Check database initialization
   - Verify service has write permissions
   - Check service logs for errors

### Getting Help

- Check Render documentation: https://render.com/docs
- View service logs in Render dashboard
- Check GitHub repository for issues

## 💡 Tips for Success

1. **Use Render's Free Tier Wisely**
   - Free services sleep after 15 minutes of inactivity
   - First request after sleep may be slow (30+ seconds)
   - Consider upgrading for production use

2. **Monitor Your Services**
   - Check Render dashboard regularly
   - Set up monitoring/alerts if needed
   - Monitor resource usage

3. **Optimize for Performance**
   - Use appropriate instance sizes
   - Consider adding caching
   - Optimize image processing

4. **Security Best Practices**
   - Use environment variables for secrets
   - Implement proper authentication
   - Regularly update dependencies

## 📝 Next Steps

After successful deployment:
1. Update your documentation with live URLs
2. Test all functionality thoroughly
3. Consider setting up monitoring
4. Plan for scaling if needed
5. Set up backups for your database

## 🔗 Useful Links

- [Render.com Documentation](https://render.com/docs)
- [Render YAML Reference](https://render.com/docs/yaml-spec)
- [Render Static Sites](https://render.com/docs/static-sites)
- [Render Web Services](https://render.com/docs/web-services)

---

**Need help?** Check the service logs in your Render dashboard or refer to the troubleshooting section above.
