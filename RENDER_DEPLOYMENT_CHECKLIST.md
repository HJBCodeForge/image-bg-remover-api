# Render Deployment Checklist

## Pre-Deployment ✅

- [ ] Code is committed and pushed to GitHub
- [ ] `requirements.txt` is complete and tested
- [ ] `render.yaml` is configured correctly
- [ ] Environment variables are documented
- [ ] CORS settings include Render domains

## Backend Deployment 🖥️

- [ ] Create Render account and connect GitHub
- [ ] Create new Web Service for backend
- [ ] Configure service settings:
  - [ ] Name: `bg-remover-api`
  - [ ] Runtime: Python 3
  - [ ] Build Command: `pip install -r requirements.txt`
  - [ ] Start Command: `python main.py`
- [ ] Set environment variables:
  - [ ] `PORT=10000`
  - [ ] `HOST=0.0.0.0`
  - [ ] `ENVIRONMENT=production`
- [ ] Deploy and wait for completion
- [ ] Test API endpoints:
  - [ ] `GET /` - API info
  - [ ] `POST /api-keys` - Generate key
  - [ ] `POST /remove-background` - Remove background
- [ ] Note API URL: `https://______.onrender.com`

## Frontend Deployment 🌐

- [ ] Create Static Site service for frontend
- [ ] Configure service settings:
  - [ ] Name: `bg-remover-frontend`
  - [ ] Build Command: `echo "No build required"`
  - [ ] Publish Directory: `.`
- [ ] Deploy and wait for completion
- [ ] Test frontend loads correctly
- [ ] Note frontend URL: `https://______.onrender.com`

## Post-Deployment Configuration 🔧

- [ ] Update API URLs in frontend files:
  - [ ] `demo.html`
  - [ ] `index.html`
  - [ ] `api-status.html`
- [ ] Use the update script:
  ```bash
  ./update_api_urls.sh https://your-api-name.onrender.com
  ```
- [ ] Commit and push changes
- [ ] Update CORS settings in `main.py` with exact frontend URL
- [ ] Redeploy backend with updated CORS settings

## Testing 🧪

- [ ] Test API directly with curl
- [ ] Test frontend at deployed URL
- [ ] Test API key generation
- [ ] Test background removal functionality
- [ ] Test CORS (frontend communicating with backend)
- [ ] Test on mobile devices
- [ ] Test with different image formats

## Troubleshooting 🔍

If issues occur:
- [ ] Check service logs in Render dashboard
- [ ] Verify environment variables are set correctly
- [ ] Check CORS configuration
- [ ] Verify API URLs are updated correctly
- [ ] Test locally first if problems persist

## Performance Optimization 🚀

- [ ] Monitor service performance
- [ ] Consider upgrading from free tier if needed
- [ ] Optimize image processing settings
- [ ] Set up monitoring/alerts
- [ ] Consider caching strategies

## Security Review 🔒

- [ ] Remove any debug/development settings
- [ ] Verify API keys are secure
- [ ] Check that sensitive data is in environment variables
- [ ] Review CORS settings for security
- [ ] Test rate limiting if implemented

## Documentation 📝

- [ ] Update README with live URLs
- [ ] Document deployment process
- [ ] Update API documentation
- [ ] Create user guide with live examples

## Final Steps ✨

- [ ] Test complete user journey
- [ ] Share live URLs with stakeholders
- [ ] Set up monitoring
- [ ] Plan for maintenance and updates
- [ ] Consider backup strategies

---

**Deployment URLs:**
- Backend API: `https://______.onrender.com`
- Frontend: `https://______.onrender.com`
- Repository: `https://github.com/______.git`

**Deployment Date:** ___________
**Deployed By:** ___________
