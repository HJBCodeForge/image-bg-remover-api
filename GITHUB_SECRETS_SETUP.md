# GitHub Secrets Setup Guide

This guide explains how to set up the required GitHub secrets for automated deployments.

## Required Secrets

### Railway (Backend API)
1. **RAILWAY_TOKEN**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click on your profile → Settings → Tokens
   - Generate a new token
   - Copy the token and add it to GitHub Secrets

2. **RAILWAY_SERVICE_ID**
   - Go to your Railway project
   - Click on your service
   - Copy the Service ID from the URL or settings
   - Add it to GitHub Secrets

### Vercel (Frontend)
1. **VERCEL_TOKEN**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Go to Settings → Tokens
   - Generate a new token
   - Copy the token and add it to GitHub Secrets

2. **VERCEL_ORG_ID**
   - Go to your Vercel team/personal settings
   - Copy the Team ID (or User ID for personal)
   - Add it to GitHub Secrets

3. **VERCEL_PROJECT_ID**
   - Go to your Vercel project settings
   - Copy the Project ID
   - Add it to GitHub Secrets

## How to Add Secrets to GitHub

1. Go to your GitHub repository
2. Click on **Settings** tab
3. Click on **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add each secret with the exact name shown above

## Testing

Once secrets are added:
1. Push changes to main branch
2. Check the **Actions** tab to see deployments
3. Both Railway and Vercel will deploy automatically

## URLs After Deployment

- **API (Railway)**: https://web-production-faaf.up.railway.app
- **Frontend (Vercel)**: https://bg-remover-frontend-tau.vercel.app

## Troubleshooting

If deployments fail:
1. Check the Actions tab for error logs
2. Verify all secrets are correctly set
3. Ensure Railway and Vercel projects are properly configured
4. Check that the URLs in the workflows match your actual deployment URLs

## Manual Deployment Commands

If needed, you can deploy manually:

```bash
# Railway
railway login
railway deploy

# Vercel
vercel login
vercel --prod
```
